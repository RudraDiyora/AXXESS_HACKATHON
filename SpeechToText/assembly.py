import requests
import time
import websocket
import numpy as np
import base64
import json
import threading

ASSEMBLYAI_REALTIME_URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
API_KEY = "e433c87a86ed446fb8e24ef96cbdeab9"
UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
headers = {"authorization": API_KEY}


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

    print(response.text)  # 👈 ADD THIS
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
    roles = ["Doctor", "Patient"]
    formatted = []

    for utt in res["utterances"]:
        speaker = utt["speaker"]

        if speaker not in speaker_map:
            speaker_map[speaker] = roles[len(speaker_map) % 2]

        role = speaker_map[speaker]
        formatted.append(f"{role}: {utt['text']}")

    return "\n".join(formatted)

class WEB:
    def __init__(self):
        self.ws = websocket.WebSocketApp(
            "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000",
            header={"Authorization": API_KEY},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )


        threading.Thread(target=self.ws.run_forever).start()

    def send_chunk_to_assembly(self, chunk: np.ndarray):
        # convert float32 -> int16
        audio_int16 = (chunk * 32767).astype('int16')
        # convert to bytes and base64 encode
        audio_bytes = audio_int16.tobytes()
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        data = json.dumps({"audio_data": audio_b64})
        self.ws.send(data)
    def on_open(ws):
        print("WebSocket connection open, start streaming audio...")

    def on_message(ws, message):
        data = json.loads(message)
        # Partial or final transcript
        if "text" in data:
            print(f"Transcript ({data.get('type', 'partial')}): {data['text']}")

    def on_error(ws, error):
        print("WebSocket error:", error)

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed")


WEB_HANDLER = WEB()

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
    print("Transcription:\n", final_text)

    result = get_transcription_result(transcript_id)
    print(format_speakers(result))