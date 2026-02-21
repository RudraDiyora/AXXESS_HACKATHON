import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import os

from openai import OpenAI
import json
import queue
import threading
import numpy as np

from assembly import WEB_HANDLER

class SPEECH_HANDLER:
    def __init__(self):
        self.sample_rate = 16000
        self.chunk_size = 2048
        self.queue = queue.Queue()
        self.accumulated_audio = []
        self.recording_object = None
        self.recording_file = None
        self.model = whisper.load_model("base")  # tiny/base/small/medium/large

    def _audio_callback(self, indata, frames, time, status):
        """This function is called for each audio block captured."""
        if status:
            print(status)
        # Flatten the audio and push it to the queue
        self.queue.put(indata.copy())

    def record_audio_live(self):
        """Start streaming audio in real-time."""
        os.makedirs("AudioFiles", exist_ok=True)
        self.recording_file = os.path.join("AudioFiles", "live_output.wav")

        # Store all chunks to save at the end
        all_chunks = []

        # Open input stream
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self._audio_callback,
            blocksize=self.chunk_size
        ):
            print("Recording... Press Ctrl+C to stop.")
            try:
                while True:
                    chunk = self.queue.get()
                    all_chunks.append(chunk)
                    # send chunk immediately to AssemblyAI
                    WEB_HANDLER.send_chunk_to_assembly(chunk)
                    # process chunk immediately
                    text = self.process_chunk(chunk=chunk)
                    print("Live transcription so far:", text)   # <--- prints real-time

                    # Here you could also send chunk directly to a translation API
                    # e.g., send_to_translator(chunk)
            except KeyboardInterrupt:
                print("Recording stopped by user.")

        # Convert to int16 and save to WAV
        recording_int16 = np.concatenate(all_chunks)
        recording_int16 = (recording_int16 * 32767).astype('int16')
        write(self.recording_file, self.sample_rate, recording_int16)
        print("Saved live recording:", self.recording_file)


        #WEB_HANDLER.ws.send(json.dumps({"terminate_session": True}))

        return self.recording_file

    def process_chunk(self, chunk: np.ndarray):
        """Append a chunk and transcribe accumulated audio."""
        # Convert stereo -> mono if needed
        if chunk.ndim > 1 and chunk.shape[1] > 1:
            chunk = np.mean(chunk, axis=1, keepdims=True)
        
        # Append chunk
        self.accumulated_audio.append(chunk)

        # Concatenate all chunks
        audio_array = np.concatenate(self.accumulated_audio, axis=0).flatten()

        # Transcribe using Whisper
        result = self.model.transcribe(audio_array, fp16=False, language="en")
        text = result["text"]
        print("Current transcription:", text)
        return text

    # static recording
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

        transcript_data = None
        with open("output_text.txt", "r") as file:
            transcript_data = file.read()


        prompt = f""" 
            You are a top tier linguist at harvard. The following text is a transcript of a 
            speech. The text is given to you in a single block. There are two 
            characters in the transcript: a doctor and a patient. The first sentence will
            always be said by the doctor. Carefully analyze the text block and predict which 
            person, whether the doctor or patient said it. Make sure the 
            categories make sense, a patient should not be reccomending medicince and the doctor 
            should not be the one listing sympotms the first time. Additionally, the doctor will 
            be asking majority if not all of the questions and the patient should have more 
            descriptive words while the doctor has more technical speak. There may be
            background noice. Only pick up the words that are clearly said. Only after reading 
            the entire text block, split the text into two paragraphs, the first 
            containing everything the doctor
            said and the second containing everything the patient says in order. The split should
            be done by ***Doctor:*** and ***Patient:****. If the time it takes you to 
            analyze the text crosses 5 minutes, return all the lines you have processed until then. 
            The transcript is: {transcript_data}

        """
        
        # recieving: {transcript_data}
        prompt2 = f"""

        """

        client = OpenAI(
            base_url="https://api.featherless.ai/v1",
            api_key="rc_dcec78432f3979ad51555b438e7927ed7ad464bccef09eeb3bc144f27f1d94d5"
        )
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.1",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        query = response.choices[0].message.content # doctor, patient
        print(query)
        doctor_speech = query.split("***Patient:***")[0].split("***Doctor:***")[1]
        patient_speech = query.split("***Patient:***")[1]

        json_injection = {
            "Doctor": str(doctor_speech),
            "Patient": str(patient_speech) 
        }

        with open("QUERY.JSON", "w") as file:
            json.dump(json_injection, file, indent=2)


# ------------------------------
testing = SPEECH_HANDLER()
testing.record_audio_live()