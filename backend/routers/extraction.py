"""
Clinical data extraction endpoints — process a transcript JSON and extract
structured medical data via LLM.

Source: Jaideep's-Branch (text_extractor.py)
"""

import json

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from services.extraction_service import (
    parse_transcript,
    build_llm_prompt,
    extract_medical_data,
    build_clinical_json,
    run_extraction,
)

router = APIRouter(prefix="/api/extract", tags=["Clinical Extraction"])


@router.post("/from-transcript")
async def extract_from_transcript(file: UploadFile = File(...)):
    """
    Accept a transcript JSON (OUTPUT.json format from speech-to-text),
    extract clinical data via LLM, and return structured medical JSON.
    """
    if file.filename and not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Only .json files are accepted.",
        )

    try:
        raw = await file.read()
        transcript_data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON.")

    messages = transcript_data.get("messages", [])
    if not messages:
        raise HTTPException(
            status_code=400,
            detail="No messages found in transcript.",
        )

    try:
        clinical_json = run_extraction(transcript_data)
        return {"status": "success", "clinical_data": clinical_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/from-json")
async def extract_from_json_body(transcript_data: dict):
    """
    Accept a transcript as a JSON body (not file upload) and extract
    clinical data.
    """
    messages = transcript_data.get("messages", [])
    if not messages:
        raise HTTPException(
            status_code=400,
            detail="No messages found in transcript.",
        )

    try:
        clinical_json = run_extraction(transcript_data)
        return {"status": "success", "clinical_data": clinical_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
