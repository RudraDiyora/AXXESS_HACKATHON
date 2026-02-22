"""
Full pipeline endpoint — upload audio → transcribe → extract clinical data
→ generate patient summary. One call does everything.

Combines: speech_to_text_WORKING + Jaideep's-Branch + Patient_Summary_Generator
"""

import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services.assembly_service import (
    upload_audio_bytes,
    submit_transcription,
    poll_transcription,
    format_speakers,
    build_transcript_json,
)
from services.extraction_service import run_extraction
from services.validator import validate_and_normalize
from services.summary_service import generate_summary
from services.post_processor import post_process

router = APIRouter(prefix="/api/pipeline", tags=["Full Pipeline"])


@router.post("/run")
async def run_full_pipeline(
    file: UploadFile = File(...),
    session_id: str = Form("session_001"),
    patient_name: str = Form("Unknown"),
    patient_age: int | None = Form(None),
):
    """
    Complete end-to-end pipeline:

    1. Upload audio → AssemblyAI transcription with speaker diarization
    2. Parse transcript into structured Doctor/Patient JSON
    3. Extract clinical data (diagnoses, ICD codes, medications) via LLM
    4. Generate patient-friendly summary via LLM
    5. Post-process: jargon replacement, HTML rendering

    Returns transcript, clinical data, summary (JSON + HTML), and metadata.
    """
    stages: dict = {}

    # ── Stage 1: Speech-to-Text ─────────────────────────────────────────
    try:
        audio_bytes = await file.read()
        audio_url = upload_audio_bytes(audio_bytes)
        transcript_id = submit_transcription(audio_url)
        result = poll_transcription(transcript_id)
        _, formatted_lines = format_speakers(result)

        patient_info = {"name": patient_name, "age": patient_age}
        transcript_json = build_transcript_json(
            formatted_lines, session_id, patient_info
        )

        stages["speech_to_text"] = {
            "status": "PASS",
            "transcript_id": transcript_id,
            "confidence": result.get("confidence"),
            "word_count": len(result.get("words", [])),
            "message_count": len(transcript_json["messages"]),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Stage 1 (Speech-to-Text) failed: {e}",
        )

    # ── Stage 2: Clinical Data Extraction ───────────────────────────────
    try:
        clinical_json = run_extraction(transcript_json)

        stages["extraction"] = {
            "status": "PASS",
            "chief_complaint": clinical_json.get("clinical_data", {}).get(
                "chief_complaint", "N/A"
            ),
            "diagnoses_count": len(
                clinical_json.get("clinical_data", {}).get("diagnoses", [])
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Stage 2 (Clinical Extraction) failed: {e}",
        )

    # ── Stage 3: Patient Summary Generation ─────────────────────────────
    try:
        validation = validate_and_normalize(clinical_json)

        if not validation["valid"]:
            raise ValueError(f"Validation errors: {validation['errors']}")

        normalized = validation["normalized"]
        raw_summary = generate_summary(normalized)
        processed = post_process(raw_summary, normalized["patient"]["name"])

        stages["summary"] = {
            "status": "PASS",
            "word_count": processed["meta"]["word_count"],
            "too_long": processed["meta"]["too_long"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Stage 3 (Summary Generation) failed: {e}",
        )

    # ── Return everything ───────────────────────────────────────────────
    return {
        "status": "success",
        "stages": stages,
        "transcript": transcript_json,
        "clinical_data": clinical_json,
        "summary": processed["summary"],
        "html": processed["html"],
        "meta": processed["meta"],
        "warnings": validation["warnings"],
    }


@router.post("/run-from-transcript")
async def run_pipeline_from_transcript(transcript_data: dict):
    """
    Run stages 2–3 from an existing transcript JSON (skip audio upload).
    Useful when the transcript is already available.
    """
    messages = transcript_data.get("messages", [])
    if not messages:
        raise HTTPException(
            status_code=400,
            detail="No messages found in transcript.",
        )

    # ── Stage 2: Clinical Data Extraction ───────────────────────────────
    try:
        clinical_json = run_extraction(transcript_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Clinical extraction failed: {e}",
        )

    # ── Stage 3: Patient Summary Generation ─────────────────────────────
    try:
        validation = validate_and_normalize(clinical_json)

        if not validation["valid"]:
            raise ValueError(f"Validation errors: {validation['errors']}")

        normalized = validation["normalized"]
        raw_summary = generate_summary(normalized)
        processed = post_process(raw_summary, normalized["patient"]["name"])

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Summary generation failed: {e}",
        )

    return {
        "status": "success",
        "transcript": transcript_data,
        "clinical_data": clinical_json,
        "summary": processed["summary"],
        "html": processed["html"],
        "meta": processed["meta"],
        "warnings": validation["warnings"],
    }
