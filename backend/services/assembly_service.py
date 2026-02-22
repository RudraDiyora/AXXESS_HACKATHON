"""
AssemblyAI integration — upload audio, transcribe with speaker diarization,
and format into structured Doctor/Patient dialogue.

Source: speech_to_text_WORKING branch (SpeechToText/assembly.py)
"""

import json
import os
import time
from pathlib import Path

import requests

from config import ASSEMBLYAI_API_KEY, ASSEMBLYAI_UPLOAD_URL, ASSEMBLYAI_TRANSCRIBE_URL

_headers = {"authorization": ASSEMBLYAI_API_KEY}


def upload_audio(file_path: str) -> str:
    """Upload an audio file to AssemblyAI and return the hosted URL."""
    with open(file_path, "rb") as f:
        response = requests.post(ASSEMBLYAI_UPLOAD_URL, headers=_headers, data=f)
    response.raise_for_status()
    return response.json()["upload_url"]


def upload_audio_bytes(audio_bytes: bytes) -> str:
    """Upload raw audio bytes to AssemblyAI and return the hosted URL."""
    response = requests.post(ASSEMBLYAI_UPLOAD_URL, headers=_headers, data=audio_bytes)
    response.raise_for_status()
    return response.json()["upload_url"]


def submit_transcription(audio_url: str) -> str:
    """Submit a transcription job with speaker diarization. Returns transcript ID."""
    json_data = {
        "audio_url": audio_url,
        "speech_models": ["universal-2"],
        "speaker_labels": True,
    }
    response = requests.post(
        ASSEMBLYAI_TRANSCRIBE_URL,
        headers={**_headers, "content-type": "application/json"},
        json=json_data,
    )
    response.raise_for_status()
    return response.json()["id"]


def poll_transcription(transcript_id: str) -> dict:
    """Poll AssemblyAI until the transcription is complete."""
    polling_url = f"{ASSEMBLYAI_TRANSCRIBE_URL}/{transcript_id}"
    while True:
        res = requests.get(polling_url, headers=_headers).json()
        if res["status"] == "completed":
            return res
        elif res["status"] == "error":
            raise RuntimeError(res["error"])
        time.sleep(1)


def format_speakers(result: dict) -> tuple[str, list[str]]:
    """
    Map AssemblyAI speaker labels to Doctor/Patient roles.
    Returns (formatted_text, list_of_lines).
    """
    if not result.get("utterances"):
        return result.get("text", ""), [result.get("text", "")]

    speaker_map: dict[str, str] = {}
    roles = ["Doctor", "Patient", "Other"]
    formatted: list[str] = []

    for utt in result["utterances"]:
        speaker = utt["speaker"]
        if speaker not in speaker_map:
            speaker_map[speaker] = roles[len(speaker_map) % 2]
        role = speaker_map[speaker]
        formatted.append(f"{role}: {utt['text']}")

    return "\n".join(formatted), formatted


def build_transcript_json(
    formatted_lines: list[str],
    session_id: str,
    patient_info: dict,
) -> dict:
    """
    Convert formatted speaker lines into the standard transcript JSON
    consumed by downstream pipeline stages.
    """
    json_data = {
        "session_id": session_id,
        "patient": {
            "name": patient_info.get("name", "Unknown"),
            "age": patient_info.get("age"),
            "preferred_language": patient_info.get("preferred_language", "en"),
        },
        "messages": [],
    }

    for line in formatted_lines:
        parts = line.split(":", 1)
        if len(parts) == 2:
            json_data["messages"].append(
                {"speaker": parts[0].strip(), "text": parts[1].strip()}
            )

    return json_data


def transcribe_audio_file(
    file_path: str,
    session_id: str = "session_001",
    patient_info: dict | None = None,
) -> dict:
    """
    High-level helper: upload → transcribe → poll → format → JSON.
    Returns the structured transcript dict.
    """
    if patient_info is None:
        patient_info = {"name": "Unknown", "age": None}

    audio_url = upload_audio(file_path)
    transcript_id = submit_transcription(audio_url)
    result = poll_transcription(transcript_id)
    _, formatted_lines = format_speakers(result)
    return build_transcript_json(formatted_lines, session_id, patient_info)
