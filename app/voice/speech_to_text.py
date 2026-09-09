from faster_whisper import WhisperModel
from app.config.settings import WHISPER_MODEL
import os

_model = None

def get_model():
    global _model
    if _model is None:
        print(f"Loading Whisper model ({WHISPER_MODEL})...")
        # Run on CPU with int8 to save memory on low-end hardware
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _model

def transcribe(audio_path: str) -> str:
    """Transcribes an audio file to text using faster-whisper."""
    if not audio_path or not os.path.exists(audio_path):
        return ""
        
    model = get_model()
    segments, _ = model.transcribe(audio_path, beam_size=1)
    
    text = " ".join([segment.text for segment in segments]).strip()
    return text
