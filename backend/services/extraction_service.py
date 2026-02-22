"""
Clinical data extraction service — parses transcripts and calls the
Featherless LLM to extract structured medical data (diagnoses, ICD codes,
medications, vitals, etc.).

Source: Jaideep's-Branch (text_extractor.py)
"""

import json
from datetime import date
from pathlib import Path

from openai import OpenAI

from config import FEATHERLESS_API_KEY, FEATHERLESS_BASE_URL
from prompts.system_prompt import build_extraction_prompt


# ── Transcript parsing ──────────────────────────────────────────────────────

def parse_transcript(transcript_data: dict) -> dict:
    """
    Parse a transcript dict into separated doctor/patient lines and an
    ordered conversation list.

    Returns dict with keys: session_id, patient, doctor_lines,
    patient_lines, conversation
    """
    session_id = transcript_data.get("session_id", "unknown_session")
    messages = transcript_data.get("messages", [])
    patient_info = transcript_data.get("patient", {})

    doctor_lines: list[str] = []
    patient_lines: list[str] = []
    conversation: list[dict] = []

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


def build_llm_prompt(conversation: list[dict]) -> str:
    """Turn the ordered conversation list into a readable string for the LLM."""
    return "\n".join(
        f"{turn['speaker']}: {turn['text']}" for turn in conversation
    )


# ── LLM extraction ─────────────────────────────────────────────────────────

def extract_medical_data(transcript_text: str) -> dict:
    """
    Call the Featherless LLM to extract structured clinical data from a
    transcript string. Returns a dict with chief_complaint, vitals,
    symptoms, diagnoses, medications_prescribed, clinician, visit_type,
    follow_up.
    """
    if not FEATHERLESS_API_KEY:
        raise RuntimeError(
            "API key not configured. Set FEATHERLESS_API_KEY in .env"
        )

    client = OpenAI(
        base_url=FEATHERLESS_BASE_URL,
        api_key=FEATHERLESS_API_KEY,
    )

    system_prompt = build_extraction_prompt()

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


# ── Build the standard clinical JSON ────────────────────────────────────────

def build_clinical_json(parsed: dict, medical_data: dict) -> dict:
    """
    Merge parsed transcript info and extracted medical data into the
    standard JSON format consumed by the summary generator.
    """
    patient_info = parsed.get("patient", {})

    return {
        "patient": {
            "name": patient_info.get("name", "Unknown"),
            "age": patient_info.get("age"),
            "preferred_language": patient_info.get("preferred_language", "en"),
        },
        "visit": {
            "date": date.today().isoformat(),
            "type": medical_data.get("visit_type", "consultation"),
            "clinician": medical_data.get("clinician", "Your care team"),
        },
        "clinical_data": {
            "chief_complaint": medical_data.get("chief_complaint", "N/A"),
            "vitals": medical_data.get("vitals", {}),
            "symptoms": medical_data.get("symptoms", []),
            "diagnoses": medical_data.get("diagnoses", []),
            "medications_prescribed": medical_data.get(
                "medications_prescribed", []
            ),
            "follow_up": medical_data.get("follow_up", "N/A"),
        },
    }


# ── Full extraction pipeline ───────────────────────────────────────────────

def run_extraction(transcript_data: dict) -> dict:
    """
    End-to-end: transcript JSON → parse → LLM extract → clinical JSON.
    Returns the standardised clinical JSON.
    """
    parsed = parse_transcript(transcript_data)
    prompt = build_llm_prompt(parsed["conversation"])
    medical = extract_medical_data(prompt)
    return build_clinical_json(parsed, medical)
