import os
import requests

def transcribe_audio_free(audio_path, api_key):
    """Transcribes audio using Groq's Whisper API with structured JSON output."""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}

    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/mp3")}
        data = {
            "model": "whisper-large-v3",
            "response_format": "verbose_json",
            "temperature": "0.0"
        }
        response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code != 200:
            raise Exception(f"Groq Transcription Error: {response.text}")
        return response.json()