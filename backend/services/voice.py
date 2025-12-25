import os
import json
import soundfile as sf
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk-model-small-en-us-0.15"

if not os.path.exists(MODEL_PATH):
    raise Exception("Vosk model not found. Download and place it in backend/models")

model = Model(MODEL_PATH)

def speech_to_text(audio_path: str) -> str:
    ext = os.path.splitext(audio_path)[1].lower()
    if ext not in [".wav", ".flac", ".ogg"]:
        raise ValueError("Invalid audio format. Please upload WAV / FLAC / OGG file.")
    
    data, samplerate = sf.read(audio_path)
    recognizer = KaldiRecognizer(model, samplerate)

    recognizer.AcceptWaveform(data.tobytes())
    result = json.loads(recognizer.Result())

    return result.get("text", "")
