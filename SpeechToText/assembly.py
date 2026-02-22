import requests
import time
import os

UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
headers = {"authorization": "0c9ce00d058341dab8c059d20c7349ac"}


def upload_file(file_path):
    with open(file_path, "rb") as f:
        response = requests.post(
            UPLOAD_URL,
            headers=headers,
            data=f
        )
    response.raise_for_status()
    return response.json()["upload_url"]


def transcribe(upload_url):
    json_data = {
        "audio_url": upload_url,
        "speech_models": ["universal-2"],   # 👈 REQUIRED NOW
        "speaker_labels": True,
     #   "speakers_expected": 2
    }

    response = requests.post(
        TRANSCRIBE_URL,
        headers={**headers, "content-type": "application/json"},
        json=json_data
    )

   # print(response.text)  # 👈 ADD THIS
    response.raise_for_status()

    return response.json()["id"]


def get_transcription_result(transcript_id):
    polling_url = f"{TRANSCRIBE_URL}/{transcript_id}"
    while True:
        res = requests.get(polling_url, headers=headers).json()
        if res["status"] == "completed":
            return res
        elif res["status"] == "error":
            raise RuntimeError(res["error"])
        time.sleep(1)
def format_speakers(res):
    if not res["utterances"]:
        return res["text"]

    speaker_map = {}
    roles = ["Doctor", "Patient", "Other"]
    formatted = []
    for utt in res["utterances"]:
        speaker = utt["speaker"]

        if speaker not in speaker_map:
            speaker_map[speaker] = roles[len(speaker_map) % 2]

        role = speaker_map[speaker]
        formatted.append(f"{role}: {utt['text']}")

    return "\n".join(formatted)

def generate_json(session_id, patient_info):
    json_data = {
        "session_id": session_id,
        "patient": {
            "name": patient_info["name"],
            "age": patient_info["age"],
            "gender": patient_info["gender"]
        },
        "messages": []
    }

if __name__ == "__main__":

    file_path = "AudioFiles/live_output.wav"
    audio_url = upload_file(file_path)
    transcript_id = transcribe(audio_url)
    print("Waiting for transcription...")

    transcript_id = transcribe(audio_url)

    if not transcript_id:
        print("Transcription failed. Stopping.")
        exit()

    final_text = get_transcription_result(transcript_id)
#   print("Transcription:\n", final_text)

    result = get_transcription_result(transcript_id)
    print(format_speakers(result))
  #  print(result.items())