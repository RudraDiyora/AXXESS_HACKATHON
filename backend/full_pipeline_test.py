"""
Full End-to-End Pipeline Test
=============================
Stage 1: Upload audio → AssemblyAI transcription with speaker diarization
Stage 2: Format transcript into structured JSON (Doctor/Patient messages)
Stage 3: Feed structured data into patient-summary-generator for final output

This test validates the complete pipeline from raw audio to patient-friendly summary.
"""

import json
import os
import sys
import time

# ─── CONFIG ─────────────────────────────────────────────────────────────────
AUDIO_FILE = os.path.join(os.path.dirname(__file__), "AudioFiles", "live_output.wav")
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "OUTPUT.json")

# Ensure patient-summary-generator imports work
SUMMARY_GEN_DIR = os.path.join(os.path.dirname(__file__), "patient-summary-generator")
sys.path.insert(0, SUMMARY_GEN_DIR)

# Load .env from patient-summary-generator
from dotenv import load_dotenv
load_dotenv(os.path.join(SUMMARY_GEN_DIR, ".env"))


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1: Speech-to-Text (AssemblyAI)
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("STAGE 1: SPEECH-TO-TEXT (AssemblyAI)")
print("=" * 70)

from SpeechToText.assembly import upload_file, transcribe, get_transcription_result, format_speakers, generate_json

print(f"[1.1] Audio file: {AUDIO_FILE}")
assert os.path.exists(AUDIO_FILE), f"Audio file not found: {AUDIO_FILE}"
print(f"      File size: {os.path.getsize(AUDIO_FILE):,} bytes")
print()

# Step 1.1: Upload audio to AssemblyAI
print("[1.2] Uploading audio to AssemblyAI...")
try:
    audio_url = upload_file(AUDIO_FILE)
    print(f"      Upload successful: {audio_url[:60]}...")
except Exception as e:
    print(f"      FAIL: Upload failed — {e}")
    sys.exit(1)
print()

# Step 1.2: Submit for transcription
print("[1.3] Submitting transcription request...")
try:
    transcript_id = transcribe(audio_url)
    print(f"      Transcript ID: {transcript_id}")
except Exception as e:
    print(f"      FAIL: Transcription request failed — {e}")
    sys.exit(1)
print()

# Step 1.3: Poll for results
print("[1.4] Waiting for transcription result (polling)...")
try:
    result = get_transcription_result(transcript_id)
    print(f"      Status: {result['status']}")
    print(f"      Confidence: {result.get('confidence', 'N/A')}")
    print(f"      Word count: {len(result.get('words', []))}")
    print(f"      Speaker count: {len(set(u['speaker'] for u in result.get('utterances', [])))}")
except Exception as e:
    print(f"      FAIL: Transcription polling failed — {e}")
    sys.exit(1)
print()

# Step 1.4: Format speakers
print("[1.5] Formatting speaker diarization...")
try:
    formatted = format_speakers(result)
    formatted_text = formatted[0]
    formatted_list = formatted[1]
    print("      Formatted transcript:")
    for line in formatted_list:
        print(f"        {line}")
except Exception as e:
    print(f"      FAIL: Speaker formatting failed — {e}")
    sys.exit(1)
print()


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2: Generate Structured JSON
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("STAGE 2: GENERATE STRUCTURED JSON")
print("=" * 70)

patient_info = {
    "name": "John Doe",
    "age": 30,
    "gender": "male"
}

print(f"[2.1] Patient info: {json.dumps(patient_info)}")

try:
    json_data = generate_json(
        formatted_list,
        "session_pipeline_test_001",
        patient_info
    )
    print(f"[2.2] Generated OUTPUT.json with {len(json_data['messages'])} messages")
    print()
    print("      Structured JSON:")
    print(json.dumps(json_data, indent=2))
except Exception as e:
    print(f"      FAIL: JSON generation failed — {e}")
    sys.exit(1)
print()


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 3: Patient Summary Generator
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("STAGE 3: PATIENT SUMMARY GENERATOR")
print("=" * 70)

from src.services.validator import validate_and_normalize
from src.services.llm_service import generate_summary
from src.services.post_processor import post_process

# Build clinical data from transcript messages
# We extract symptoms/chief complaint from the patient's messages
patient_messages = [m["text"].strip() for m in json_data["messages"] if m["speaker"] == "Patient"]
doctor_messages = [m["text"].strip() for m in json_data["messages"] if m["speaker"] == "Doctor"]

chief_complaint = " ".join(patient_messages) if patient_messages else "General consultation"

# Build the input payload for the summary generator
summary_input = {
    "patient": {
        "name": patient_info["name"],
        "age": patient_info["age"],
        "preferred_language": "en"
    },
    "visit": {
        "date": "2026-02-22",
        "type": "consultation",
        "clinician": "Your care team"
    },
    "clinical_data": {
        "chief_complaint": chief_complaint,
        "vitals": {
            "bp": None,
            "hr": None,
            "temp": None,
            "o2_sat": None
        },
        "symptoms": patient_messages,
        "diagnoses": [],
        "medications_prescribed": [],
        "follow_up": "Follow up as needed based on doctor's recommendation"
    }
}

# Step 3.1: Validate
print("[3.1] Validating summary input...")
validation = validate_and_normalize(summary_input)
print(f"      Valid: {validation['valid']}")
print(f"      Errors: {validation['errors']}")
print(f"      Warnings: {validation['warnings']}")

if not validation["valid"]:
    print("      FAIL: Validation failed")
    sys.exit(1)
print()

normalized = validation["normalized"]

# Step 3.2: Generate summary via LLM
model = os.environ.get("FEATHERLESS_MODEL", "deepseek-ai/DeepSeek-V3-0324")
api_key = os.environ.get("FEATHERLESS_API_KEY", "")
print(f"[3.2] Calling LLM ({model})...")
print(f"      API key loaded: {'yes' if api_key else 'NO — check .env file'}")

try:
    raw_summary = generate_summary(normalized)
    print("      LLM response received successfully!")
    print()
    print("      Raw LLM Output:")
    print(json.dumps(raw_summary, indent=2))
except Exception as e:
    print(f"      FAIL: LLM call failed — {e}")
    sys.exit(1)
print()

# Step 3.3: Post-process
print("[3.3] Post-processing summary (jargon replacement, HTML rendering)...")
try:
    processed = post_process(raw_summary, normalized["patient"]["name"])
    print("      Post-processing complete!")
except Exception as e:
    print(f"      FAIL: Post-processing failed — {e}")
    sys.exit(1)
print()


# ═══════════════════════════════════════════════════════════════════════════
# FINAL OUTPUT
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("FINAL OUTPUT: PATIENT-FRIENDLY VISIT SUMMARY")
print("=" * 70)
print()

print("--- Summary JSON ---")
print(json.dumps(processed["summary"], indent=2))
print()

print(f"--- Meta ---")
print(f"Word count: {processed['meta']['word_count']}")
print(f"Too long: {processed['meta']['too_long']}")
print(f"Flags: {processed['meta']['flagged']}")
print()

print("--- HTML Output ---")
print(processed["html"])
print()

# Save final output
final_output = {
    "pipeline_test": True,
    "timestamp": "2026-02-22",
    "stages": {
        "stage_1_speech_to_text": {
            "status": "PASS",
            "audio_file": AUDIO_FILE,
            "transcript_id": transcript_id,
            "speaker_count": len(set(u["speaker"] for u in result.get("utterances", []))),
            "word_count": len(result.get("words", [])),
        },
        "stage_2_structured_json": {
            "status": "PASS",
            "message_count": len(json_data["messages"]),
            "session_id": json_data["session_id"],
        },
        "stage_3_patient_summary": {
            "status": "PASS",
            "model": model,
            "word_count": processed["meta"]["word_count"],
            "too_long": processed["meta"]["too_long"],
        },
    },
    "transcript": json_data,
    "summary": processed["summary"],
    "html": processed["html"],
}

output_path = os.path.join(os.path.dirname(__file__), "PIPELINE_TEST_OUTPUT.json")
with open(output_path, "w") as f:
    json.dump(final_output, f, indent=2)
print(f"Full test output saved to: {output_path}")

# Save HTML output
html_path = os.path.join(os.path.dirname(__file__), "PIPELINE_TEST_OUTPUT.html")
with open(html_path, "w") as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Patient Visit Summary — Pipeline Test</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; color: #333; }}
        h2 {{ color: #1a73e8; }}
        h3 {{ color: #555; margin-top: 24px; }}
        .patient-summary {{ background: #f8f9fa; padding: 24px; border-radius: 12px; border: 1px solid #e0e0e0; }}
        .greeting {{ font-size: 1.1em; color: #1a73e8; font-weight: 500; }}
        .closing {{ font-style: italic; color: #666; margin-top: 16px; }}
        .meta {{ margin-top: 20px; padding: 12px; background: #fff3cd; border-radius: 8px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h2>Patient Visit Summary</h2>
    <p><strong>Patient:</strong> {patient_info['name']} | <strong>Date:</strong> 2026-02-22</p>
    {processed['html']}
    <div class="meta">
        <strong>Meta:</strong> Word count: {processed['meta']['word_count']} | 
        Flags: {', '.join(processed['meta']['flagged']) if processed['meta']['flagged'] else 'None'}
    </div>
</body>
</html>""")
print(f"HTML output saved to: {html_path}")

print()
print("=" * 70)
print("ALL PIPELINE STAGES PASSED")
print("=" * 70)
