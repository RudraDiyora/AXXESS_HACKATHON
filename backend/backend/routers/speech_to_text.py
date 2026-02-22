"""
Speech-to-Text endpoints — upload audio and get a structured transcript.

Source: speech_to_text_WORKING branch
"""

import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.assembly_service import (
    transcribe_audio_file,
    upload_audio_bytes,
    submit_transcription,
    poll_transcription,
    format_speakers,
    build_transcript_json,
)

router = APIRouter(prefix="/api/speech-to-text", tags=["Speech-to-Text"])


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    session_id: str = "session_001",
    patient_name: str = "Unknown",
    patient_age: int | None = None,
):
    """
    Upload an audio file (WAV, MP3, etc.), transcribe via AssemblyAI with
    speaker diarization, and return structured Doctor/Patient JSON.
    """
    allowed = {
        "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3",
        "audio/mp4", "audio/ogg", "audio/webm", "audio/flac",
        "application/octet-stream",  # fallback for unknown types
    }

    if file.content_type and file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio type: {file.content_type}",
        )

    try:
        audio_bytes = await file.read()

        # Upload to AssemblyAI
        audio_url = upload_audio_bytes(audio_bytes)

        # Submit transcription
        transcript_id = submit_transcription(audio_url)

        # Poll for result
        result = poll_transcription(transcript_id)

        # Format speakers
        _, formatted_lines = format_speakers(result)

        # Build structured JSON
        patient_info = {"name": patient_name, "age": patient_age}
        transcript_json = build_transcript_json(
            formatted_lines, session_id, patient_info
        )

        return {
            "status": "success",
            "transcript_id": transcript_id,
            "confidence": result.get("confidence"),
            "word_count": len(result.get("words", [])),
            "transcript": transcript_json,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
