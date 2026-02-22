from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from openai import OpenAI
import os
import json
import subprocess
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

class MedicationPrescribed(BaseModel):
    name: str = Field(description="Medication name")
    dose: str = Field(default="", description="Dosage amount, e.g. '10mg', '500mg'")
    frequency: str = Field(description="Dosage frequency, e.g. 'once daily', 'twice daily'")
    purpose: str = Field(default="", description="Reason for prescribing, e.g. 'pain relief'")

class Diagnosis(BaseModel):
    description: str = Field(description="Diagnosis or condition name")
    icd_code: str = Field(default="", description="ICD-10 code if applicable")
    confidence: float = Field(default=0.0, description="Confidence score 0-1")

class Vitals(BaseModel):
    bp: str = Field(default="N/A", description="Blood pressure, e.g. '120/80'")
    hr: int | None = Field(default=None, description="Heart rate in bpm")
    temp: float | None = Field(default=None, description="Temperature in °F")
    o2_sat: int | None = Field(default=None, description="Oxygen saturation percentage")

class ClinicalData(BaseModel):
    chief_complaint: str = Field(description="Primary reason for the visit")
    vitals: Vitals = Field(default_factory=Vitals)
    symptoms: list[str] = Field(description="List of symptoms mentioned by the patient")
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    medications_prescribed: list[MedicationPrescribed] = Field(default_factory=list)
    follow_up: str = Field(description="Instructions for follow-up care")

class VisitInfo(BaseModel):
    date: str = Field(default_factory=lambda: date.today().isoformat())
    type: str = Field(default="consultation")
    clinician: str = Field(default="Your care team")

class PatientInfo(BaseModel):
    name: str = Field(default="Unknown", description="Patient full name")
    age: int | None = Field(default=None, description="Patient age")
    preferred_language: str = Field(default="en", description="Preferred language code")

class ExtractedMedicalData(BaseModel):
    patient: PatientInfo = Field(default_factory=PatientInfo)
    visit: VisitInfo = Field(default_factory=VisitInfo)
    clinical_data: ClinicalData = Field(default_factory=ClinicalData)


# ---------------------------------------------------------------------------
# Core helpers (importable by test_runner and other pipeline stages)
# ---------------------------------------------------------------------------

def parse_transcript(transcript_data: dict) -> dict:
    """
    Parse a transcript dict into separated doctor/patient lines and an ordered
    conversation list.

    Returns a dict with keys: session_id, patient, doctor_lines, patient_lines, conversation
    """
    session_id = transcript_data.get("session_id", "unknown_session")
    messages = transcript_data.get("messages", [])

    # Extract patient info if present in the input
    patient_info = transcript_data.get("patient", {})

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
        "patient": patient_info,
        "doctor_lines": doctor_lines,
        "patient_lines": patient_lines,
        "conversation": conversation,
    }


def save_session_files(parsed: dict, output_dir: Path) -> dict:
    """
    Save doctor log, patient log, and the main output JSON into *output_dir*.
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

    # Build main output file matching the Patient_Summary_Generator contract
    clinical = parsed.get("extracted_medical_data", {})
    patient_info = parsed.get("patient", {})

    output_json = {
        "patient": {
            "name": patient_info.get("name", "Unknown"),
            "age": patient_info.get("age"),
            "preferred_language": patient_info.get("preferred_language", "en"),
        },
        "visit": {
            "date": date.today().isoformat(),
            "type": clinical.get("visit_type", "consultation"),
            "clinician": clinical.get("clinician", "Your care team"),
        },
        "clinical_data": {
            "chief_complaint": clinical.get("chief_complaint", "N/A"),
            "vitals": clinical.get("vitals", {}),
            "symptoms": clinical.get("symptoms", []),
            "diagnoses": clinical.get("diagnoses", []),
            "medications_prescribed": clinical.get("medications_prescribed", []),
            "follow_up": clinical.get("follow_up", "N/A"),
        },
    }

    comp_path = output_dir / f"session_{sid}.json"
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2, ensure_ascii=False)

    return {"doctor_log": str(doc_path), "patient_log": str(pat_path), "session_output": str(comp_path), "output_json": output_json}


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
        "with these exact keys:\n"
        "  chief_complaint (string — the primary reason for the visit),\n"
        "  vitals (object with keys: bp (string like '120/80'), hr (integer bpm), "
        "temp (float °F), o2_sat (integer %)),\n"
        "  symptoms (list of short strings),\n"
        "  diagnoses (list of objects, each with 'description' (string — the condition name), "
        "'icd_code' (string — the ICD-10 code, e.g. 'J02.0' for strep pharyngitis), "
        "and 'confidence' (float 0-1 — your confidence in this diagnosis)),\n"
        "  medications_prescribed (list of objects, each with 'name' (string), "
        "'dose' (string like '500mg' or empty string if unknown), "
        "'frequency' (string like 'once daily'), "
        "and 'purpose' (string — brief reason for the medication)),\n"
        "  clinician (string — the doctor's name if mentioned, otherwise 'Your care team'),\n"
        "  visit_type (string — e.g. 'consultation', 'follow-up', 'urgent care'),\n"
        "  follow_up (string).\n"
        "If a vital is not mentioned, use null. "
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


def print_medical_report(session_id: str, medical_data: dict, patient_info: dict | None = None):
    """Pretty-print the extracted medical data to the console."""
    print("\n" + "=" * 70)
    print("MEDICAL CONSULTATION ANALYSIS REPORT")
    print("=" * 70)
    print(f"\nSession ID: {session_id}")

    if patient_info:
        print(f"\nPATIENT:")
        print(f"  Name    : {patient_info.get('name', 'Unknown')}")
        print(f"  Age     : {patient_info.get('age', 'N/A')}")
        print(f"  Language: {patient_info.get('preferred_language', 'en')}")

    print(f"\nCHIEF COMPLAINT:\n  {medical_data.get('chief_complaint', 'N/A')}")

    print("\nSYMPTOMS:")
    for s in medical_data.get("symptoms", []):
        print(f"  - {s}")

    print("\nDIAGNOSES:")
    for dx in medical_data.get("diagnoses", []):
        if isinstance(dx, dict):
            icd = dx.get('icd_code', '')
            conf = dx.get('confidence', '')
            tag = f" [{icd}]" if icd else ""
            score = f" (confidence: {conf})" if conf else ""
            print(f"  - {dx.get('description', '?')}{tag}{score}")
        else:
            print(f"  - {dx}")

    print("\nMEDICATIONS PRESCRIBED:")
    for med in medical_data.get("medications_prescribed", []):
        if isinstance(med, dict):
            dose = f" {med['dose']}" if med.get('dose') else ""
            purpose = f" — {med['purpose']}" if med.get('purpose') else ""
            print(f"  - {med.get('name', '?')}{dose} ({med.get('frequency', '?')}){purpose}")
        else:
            print(f"  - {med}")

    print(f"\nFOLLOW-UP:\n  {medical_data.get('follow_up', 'N/A')}")

    clinician = medical_data.get("clinician", "Your care team")
    visit_type = medical_data.get("visit_type", "consultation")
    print(f"\nVISIT: {visit_type} | Clinician: {clinician}")

    vitals = medical_data.get("vitals", {})
    print("\nVITALS:")
    print(f"  BP     : {vitals.get('bp', 'N/A')}")
    print(f"  HR     : {vitals.get('hr', 'N/A')}")
    print(f"  Temp   : {vitals.get('temp', 'N/A')}")
    print(f"  O2 Sat : {vitals.get('o2_sat', 'N/A')}")
    print("=" * 70)


def send_to_patient_summary_branch(output_json: dict, repo_root: Path | None = None):
    """
    Commit initial_file.json to the Patient_Summary_Generator branch at
    patient-summary-generator/src/data/initial_file.json using a temporary
    git worktree (no branch-switching required on the main working tree).
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent

    worktree_dir = repo_root / ".tmp_psg_worktree"
    target_rel = "patient-summary-generator/src/data/initial_file.json"
    branch = "Patient_Summary_Generator"

    def _run(cmd, cwd=None):
        return subprocess.run(
            cmd, cwd=str(cwd or repo_root),
            capture_output=True, text=True,
        )

    try:
        # Clean up stale worktree ref if it exists
        _run(["git", "worktree", "prune"])

        if worktree_dir.exists():
            _run(["git", "worktree", "remove", str(worktree_dir), "--force"])

        # Create temp worktree for the target branch
        result = _run(["git", "worktree", "add", str(worktree_dir), branch])
        if result.returncode != 0:
            print(f"  [!] Could not create worktree: {result.stderr.strip()}")
            return False

        # Write the file
        dest = worktree_dir / target_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=2, ensure_ascii=False)

        # Stage + commit + push
        _run(["git", "add", target_rel], cwd=worktree_dir)

        commit = _run(
            ["git", "commit", "-m", "Auto-update initial_file.json from text_extractor pipeline"],
            cwd=worktree_dir,
        )
        if commit.returncode != 0:
            if "nothing to commit" in commit.stdout:
                print("  [i] initial_file.json unchanged — nothing to commit.")
                return True
            print(f"  [!] Commit failed: {commit.stderr.strip()}")
            return False

        push = _run(["git", "push", "origin", branch], cwd=worktree_dir)
        if push.returncode != 0:
            print(f"  [!] Push failed: {push.stderr.strip()}")
            return False

        print(f"  [ok] Pushed initial_file.json -> origin/{branch}")
        return True

    except Exception as e:
        print(f"  [!] send_to_patient_summary_branch error: {e}")
        return False

    finally:
        # Always clean up the worktree
        _run(["git", "worktree", "remove", str(worktree_dir), "--force"])


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
        print_medical_report(parsed["session_id"], medical, parsed.get("patient"))

        # Auto-send initial_file.json to Patient_Summary_Generator branch
        output_json = saved_paths.pop("output_json")
        send_to_patient_summary_branch(output_json)

        return {
            "status": "success",
            "files_saved": saved_paths,
            "clinical_data": medical,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))