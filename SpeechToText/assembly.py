import requests
import time
import os
import json

UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
headers = {"authorization": os.getenv("API_KEY")}


def upload_file(file_path):
    """Upload an audio file to AssemblyAI and return the hosted URL."""
    with open(file_path, "rb") as f:
        response = requests.post(
            UPLOAD_URL,
            headers=headers,
            data=f
        )
    response.raise_for_status()
    return response.json()["upload_url"]


def transcribe(upload_url):
    """Submit a transcription job with speaker diarization enabled."""
    json_data = {
        "audio_url": upload_url,
        "speech_model": "best",
        "speaker_labels": True,
        "speakers_expected": 2
    }

    response = requests.post(
        TRANSCRIBE_URL,
        headers={**headers, "content-type": "application/json"},
        json=json_data
    )
    response.raise_for_status()

    result = response.json()
    print(f"Transcription job submitted: {result['id']}")
    return result["id"]


def get_transcription_result(transcript_id):
    """Poll until the transcription is complete and return the result."""
    polling_url = f"{TRANSCRIBE_URL}/{transcript_id}"
    while True:
        res = requests.get(polling_url, headers=headers).json()
        status = res.get("status")
        if status == "completed":
            return res
        elif status == "error":
            raise RuntimeError(f"Transcription failed: {res.get('error', 'Unknown error')}")
        print(f"  Status: {status} — polling again in 3s...")
        time.sleep(3)


def format_speakers(res):
    """
    Split the transcript into Doctor and Patient lines based on speaker
    diarization. The first speaker detected is assumed to be the Doctor.
    Returns a formatted string and a dict with separated text.
    """
    utterances = res.get("utterances")
    if not utterances:
        # No diarization data — return plain text
        plain = res.get("text", "")
        return plain, {"Doctor": plain, "Patient": ""}

    speaker_map = {}
    roles = ["Doctor", "Patient"]
    formatted_lines = []
    doctor_lines = []
    patient_lines = []

    for utt in utterances:
        speaker = utt["speaker"]

        # Assign roles in order of first appearance (first speaker = Doctor)
        if speaker not in speaker_map:
            if len(speaker_map) < 2:
                speaker_map[speaker] = roles[len(speaker_map)]
            else:
                # More than 2 speakers detected — assign to Patient
                speaker_map[speaker] = "Patient"

        role = speaker_map[speaker]
        formatted_lines.append(f"{role}: {utt['text']}")

        if role == "Doctor":
            doctor_lines.append(utt["text"])
        else:
            patient_lines.append(utt["text"])

    formatted_text = "\n".join(formatted_lines)
    split_dict = {
        "Doctor": " ".join(doctor_lines),
        "Patient": " ".join(patient_lines)
    }
    return formatted_text, split_dict


if __name__ == "__main__":
    file_path = "AudioFiles/live_output.wav"

    if not os.path.exists(file_path):
        print(f"Error: Audio file not found at '{file_path}'")
        exit(1)

    # Step 1: Upload
    print(f"Uploading '{file_path}'...")
    audio_url = upload_file(file_path)
    print(f"Upload complete: {audio_url}")

    # Step 2: Transcribe (single call)
    transcript_id = transcribe(audio_url)
    print("Waiting for transcription...")

    if not transcript_id:
        print("Transcription failed. Stopping.")
        exit(1)

    # Step 3: Poll for result (single call)
    result = get_transcription_result(transcript_id)
    print("\n--- Raw Transcription ---")
    print(result.get("text", ""))

    # Step 4: Format into Doctor / Patient
    formatted_text, split_dict = format_speakers(result)
    print("\n--- Speaker-Split Transcription ---")
    print(formatted_text)

    # Step 5: Save outputs
    with open("output_text.txt", "w") as f:
        f.write(formatted_text)
    print("\nSaved formatted transcript to output_text.txt")

    with open("QUERY.JSON", "w") as f:
        json.dump(split_dict, f, indent=2)
    print("Saved Doctor/Patient split to QUERY.JSON")