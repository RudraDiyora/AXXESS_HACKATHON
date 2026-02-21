import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import os
import requests

class SPEECH_HANDLER():
    def __init__(self):
        self.sample_rate = 16000
        self.recording_object = None
        self.recording_file = None
        self.model = whisper.load_model("base")  # tiny/base/small/medium/large


    def record_audio(self, duration) -> list:
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1
        )
        sd.wait()

        # convert float32 -> int16 for WAV
        recording_int16 = (recording * 32767).astype('int16')

        os.makedirs("AudioFiles", exist_ok=True)
        file_path = os.path.join("AudioFiles", "output.wav")
        write(file_path, self.sample_rate, recording_int16)
        print("Saved file successfully:", file_path)

        self.recording_object = recording_int16
        self.recording_file = file_path

        return [recording, file_path]

    def speech_to_text(self) -> str:
        print("Transcribing with Whisper...")
        result = self.model.transcribe(self.recording_file)
        text = result["text"]
        print("Transcription complete.")


        with open("output_text.txt", "w") as file:
            file.write(text)
        return text
    
    def seperate_text(self):
        response = requests.post(
            url="https://api.featherless.ai/v1/deepseek-ai/DeepSeek-V3.2",
            headers={
                "Authorization": "rc_dcec78432f3979ad51555b438e7927ed7ad464bccef09eeb3bc144f27f1d94d5"
            },
            json={
                "model": "deepseek-ai/DeepSeek-V3-0324",
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ]
            }
        )
        print(response.json())


# ------------------------------
testing = SPEECH_HANDLER()
testing.record_audio(5)  # record 3 seconds
print(testing.speech_to_text())
testing.speech_to_text()