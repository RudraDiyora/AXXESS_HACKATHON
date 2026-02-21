from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from openai import OpenAI
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

class ExtractedMedicalData(BaseModel):
    symptoms: list[str] = Field(description="List of symptoms mentioned by the patient")
    diagnosis: str = Field(description="The primary diagnosis or suspected condition")
    prescriptions: list[str] = Field(description="Any medications or treatments prescribed")
    follow_up: str = Field(description="Instructions for follow-up care")
    vitals: dict = Field(default_factory=dict, description="Patient vitals: temperature, blood_pressure, o2_level, weight")


# ---------------------------------------------------------------------------
# Core helpers (importable by test_runner and other pipeline stages)
# ---------------------------------------------------------------------------

def parse_transcript(transcript_data: dict) -> dict:
    """
    Parse a transcript dict into separated doctor/patient lines and an ordered
    conversation list.

    Returns a dict with keys: session_id, doctor_lines, patient_lines, conversation
    """
    session_id = transcript_data.get("session_id", "unknown_session")
    messages = transcript_data.get("messages", [])

    doctor_lines: list[str] = []
    patient_lines: list[str] = []
    conversation: list[dict] = []        # ordered record of every turn

    for msg in messages:
        if not isinstance(msg, dict):
            continue

        speaker = msg.get("speaker", "").lower().strip()
        text = msg.get("text", "").strip()

        if not speaker or not text:
            continue

        if speaker in ("doctor", "dr", "physician", "doc"):
            speaker_normalized = "Doctor"
            doctor_lines.append(text)
        elif speaker in ("patient", "pt", "p"):
            speaker_normalized = "Patient"
            patient_lines.append(text)
        else:
            continue

        conversation.append({"speaker": speaker_normalized, "text": text})

    return {
        "session_id": session_id,
        "doctor_lines": doctor_lines,
        "patient_lines": patient_lines,
        "conversation": conversation,
    }


def save_session_files(parsed: dict, output_dir: Path) -> dict:
    """
    Save doctor log, patient log, and comprehensive JSON into *output_dir*.
    Returns a dict of the three file paths.
    
    Note: extracted_medical_data should be added to parsed before calling if available.
    """
    output_dir.mkdir(exist_ok=True)
    sid = parsed["session_id"]

    doctor_log = {"session_id": sid, "speaker": "Doctor",  "dialogue": parsed["doctor_lines"]}
    patient_log = {"session_id": sid, "speaker": "Patient", "dialogue": parsed["patient_lines"]}

    doc_path = output_dir / f"doctor_log_{sid}.json"
    pat_path = output_dir / f"patient_log_{sid}.json"

    with open(doc_path, "w", encoding="utf-8") as f:
        json.dump(doctor_log, f, indent=2, ensure_ascii=False)
    with open(pat_path, "w", encoding="utf-8") as f:
        json.dump(patient_log, f, indent=2, ensure_ascii=False)

    # Build comprehensive file
    comprehensive = {
        "session_id": sid,
        "extraction_status": "success",
        "doctor_dialogue": parsed["doctor_lines"],
        "patient_dialogue": parsed["patient_lines"],
        "conversation": parsed["conversation"],
        "extracted_medical_data": parsed.get("extracted_medical_data", {}),
    }

    comp_path = output_dir / f"session_{sid}_comprehensive.json"
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump(comprehensive, f, indent=2, ensure_ascii=False)

    return {"doctor_log": str(doc_path), "patient_log": str(pat_path), "comprehensive_report": str(comp_path)}


def build_llm_prompt(conversation: list[dict]) -> str:
    """Turn the ordered conversation list into a readable string for the LLM."""
    return "\n".join(f"{turn['speaker']}: {turn['text']}" for turn in conversation)


def extract_medical_data(transcript_text: str) -> dict:
    """
    Call the Featherless LLM and return a dict matching ExtractedMedicalData fields.
    """
    api_key = os.getenv("FEATHERLESS_API_KEY")
    if not api_key:
        raise RuntimeError("API key not configured. Set FEATHERLESS_API_KEY in environment.")

    client = OpenAI(
        base_url="https://api.featherless.ai/v1",
        api_key=api_key,
    )

    system_prompt = (
        "You are a clinical NLP assistant. "
        "Extract the following from the provided transcript and return ONLY valid JSON "
        "with these exact keys: symptoms (list of strings), diagnosis (string), "
        "prescriptions (list of strings), follow_up (string), "
        "vitals (object with keys: temperature, blood_pressure, o2_level, weight). "
        "For each vital, use the value mentioned in the transcript or null if not mentioned. "
        "Do not include any text outside the JSON object."
    )

    response = client.chat.completions.create(
        model="mistralai/Mistral-Nemo-Instruct-2407",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript_text},
        ],
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


def print_medical_report(session_id: str, medical_data: dict):
    """Pretty-print the extracted medical data to the console."""
    print("\n" + "=" * 70)
    print("MEDICAL CONSULTATION ANALYSIS REPORT")
    print("=" * 70)
    print(f"\nSession ID: {session_id}")

    print("\nSYMPTOMS:")
    for s in medical_data.get("symptoms", []):
        print(f"  - {s}")

    print(f"\nDIAGNOSIS:\n  {medical_data.get('diagnosis', 'N/A')}")

    print("\nPRESCRIPTIONS / MEDICATIONS:")
    for p in medical_data.get("prescriptions", []):
        print(f"  - {p}")

    print(f"\nFOLLOW-UP INSTRUCTIONS:\n  {medical_data.get('follow_up', 'N/A')}")

    vitals = medical_data.get("vitals", {})
    print("\nPATIENT VITALS:")
    print(f"  Temperature   : {vitals.get('temperature', 'N/A')}")
    print(f"  Blood Pressure: {vitals.get('blood_pressure', 'N/A')}")
    print(f"  O2 Level      : {vitals.get('o2_level', 'N/A')}")
    print(f"  Weight        : {vitals.get('weight', 'N/A')}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# FastAPI endpoint
# ---------------------------------------------------------------------------

@app.post("/process-json-transcript/")
async def process_json_transcript(file: UploadFile = File(...)):
    """
    Accepts a JSON transcript, separates doctor/patient dialogue into files,
    calls the LLM for medical extraction, and returns everything as JSON.
    """
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are accepted.")

    try:
        file_contents = await file.read()
        transcript_data = json.loads(file_contents)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file formatting.")

    messages = transcript_data.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="No messages found in transcript.")

    try:
        # Parse
        parsed = parse_transcript(transcript_data)

        # LLM extraction
        prompt_text = build_llm_prompt(parsed["conversation"])
        medical = extract_medical_data(prompt_text)
        parsed["extracted_medical_data"] = medical

        # Save files
        output_dir = Path("transcripts")
        saved_paths = save_session_files(parsed, output_dir)

        # Print to console
        print_medical_report(parsed["session_id"], medical)

        return {
            "status": "success",
            "files_saved": saved_paths,
            "clinical_notes": medical,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))