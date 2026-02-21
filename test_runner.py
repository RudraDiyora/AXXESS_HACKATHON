"""
Test script — exercises the core text_extractor pipeline end-to-end
using test_file.json.  The LLM call is mocked so no API key is needed.
"""
import json
from pathlib import Path

# Import the reusable helpers from text_extractor
from text_extractor import (
    parse_transcript,
    save_session_files,
    build_llm_prompt,
    print_medical_report,
)

TEST_FILE = Path("test_file.json")
OUTPUT_DIR = Path("transcripts")


def run_tests():
    print("=" * 70)
    print("TESTING TEXT EXTRACTOR PIPELINE")
    print("=" * 70)

    # --- 1. Load input JSON ---
    print("\n1. Loading test_file.json ...")
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        transcript_data = json.load(f)

    session_id = transcript_data.get("session_id", "unknown_session")
    messages = transcript_data.get("messages", [])
    print(f"   Session : {session_id}")
    print(f"   Messages: {len(messages)}")
    assert messages, "No messages found in test file!"

    # --- 2. Parse transcript ---
    print("\n2. Parsing transcript ...")
    parsed = parse_transcript(transcript_data)
    print(f"   Doctor lines : {len(parsed['doctor_lines'])}")
    print(f"   Patient lines: {len(parsed['patient_lines'])}")
    print(f"   Conversation turns: {len(parsed['conversation'])}")
    assert len(parsed["doctor_lines"]) == 6, f"Expected 6 doctor lines, got {len(parsed['doctor_lines'])}"
    assert len(parsed["patient_lines"]) == 5, f"Expected 5 patient lines, got {len(parsed['patient_lines'])}"
    assert len(parsed["conversation"]) == 11, f"Expected 11 turns, got {len(parsed['conversation'])}"

    # --- 3. Build LLM prompt ---
    print("\n3. Building LLM prompt ...")
    prompt = build_llm_prompt(parsed["conversation"])
    assert prompt.startswith("Doctor:"), "Prompt should start with Doctor:"
    print(f"   Prompt length: {len(prompt)} chars")
    print(f"   First line   : {prompt.splitlines()[0]}")

    # --- 4. Mock LLM extraction (no API key needed) ---
    print("\n4. Using mock medical extraction (LLM skipped for test) ...")
    mock_medical = {
        "symptoms": [
            "Sudden and severe throat pain",
            "Fever",
            "Painful swallowing",
            "Swollen, tender lymph nodes in neck",
            "Red and swollen tonsils with white spots",
        ],
        "diagnosis": "Strep Throat (Positive rapid test)",
        "prescriptions": [
            "Oral amoxicillin for 10 days",
            "Over-the-counter Ibuprofen for fever",
        ],
        "follow_up": (
            "Get plenty of rest and drink lots of fluids. "
            "Return to regular activities 24 hours after first antibiotic dose if no fever. "
            "Call office if symptoms don't improve after a couple of days."
        ),
    }
    parsed["extracted_medical_data"] = mock_medical

    # --- 5. Save output files ---
    print("\n5. Saving JSON output files ...")
    saved = save_session_files(parsed, OUTPUT_DIR)
    for label, path in saved.items():
        assert Path(path).exists(), f"File not created: {path}"
        print(f"   {label}: {path}")

    # --- 6. Verify comprehensive JSON content ---
    print("\n6. Verifying comprehensive JSON ...")
    comp_path = Path(saved["comprehensive_report"])
    with open(comp_path, "r", encoding="utf-8") as f:
        comp = json.load(f)

    assert comp["session_id"] == session_id
    assert len(comp["doctor_dialogue"]) == 6
    assert len(comp["patient_dialogue"]) == 5
    assert len(comp["conversation"]) == 11
    assert comp["extracted_medical_data"]["diagnosis"] == mock_medical["diagnosis"]
    print("   All fields verified.")

    # --- 7. Print report ---
    print_medical_report(session_id, mock_medical)

    # --- 8. Show generated JSON ---
    print("\n--- DOCTOR LOG ---")
    doc_log = json.loads(Path(saved["doctor_log"]).read_text(encoding="utf-8"))
    print(json.dumps(doc_log, indent=2))

    print("\n--- PATIENT LOG ---")
    pat_log = json.loads(Path(saved["patient_log"]).read_text(encoding="utf-8"))
    print(json.dumps(pat_log, indent=2))

    print("\n--- COMPREHENSIVE (excerpt) ---")
    print(json.dumps(comp, indent=2)[:600] + "\n  ... [truncated]")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
