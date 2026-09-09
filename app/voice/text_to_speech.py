import subprocess
import os
from pathlib import Path
from app.config.settings import TTS_ENABLED, PIPER_MODEL_PATH

def speak(text: str):
    """Speaks the text using Piper TTS via subprocess."""
    if not TTS_ENABLED:
        print(f"Jarvis: {text}")
        return
        
    piper_exe = Path(PIPER_MODEL_PATH).parent / "piper.exe"
    
    if not piper_exe.exists() or not Path(PIPER_MODEL_PATH).exists():
        print(f"Jarvis: {text}")
        print("[Warning] Piper TTS missing. Did you run setup_windows.bat?")
        return
        
    print(f"Jarvis: {text}")
    try:
        # Echo text into piper executable
        cmd = f'echo {text} | "{piper_exe}" --model "{PIPER_MODEL_PATH}" --output_raw | bplay -S 22050 -B 16 -c 1'
        # bplay might not exist on Windows, so a robust way is to save to wav and play
        
        wav_path = Path(__file__).parent.parent.parent / "data" / "output.wav"
        cmd = f'echo {text} | "{piper_exe}" --model "{PIPER_MODEL_PATH}" --output_file "{wav_path}"'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if wav_path.exists():
            import winsound
            winsound.PlaySound(str(wav_path), winsound.SND_FILENAME)
            wav_path.unlink()
    except Exception as e:
        print(f"[Warning] Failed to play TTS: {e}")
