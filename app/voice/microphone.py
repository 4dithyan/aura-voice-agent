import sounddevice as sd
import numpy as np
import wave
import tempfile
import time
from pathlib import Path

# Parameters for recording
SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 0.02
SILENCE_DURATION = 1.5  # Seconds of silence to stop recording

def record_audio(output_path: str = None) -> str:
    """
    Records audio from the microphone until silence is detected.
    Returns the path to the recorded WAV file.
    """
    print("Listening...")
    
    if output_path is None:
        temp_dir = Path(tempfile.gettempdir())
        output_path = temp_dir / "jarvis_input.wav"
        
    recorded_frames = []
    silent_frames = 0
    is_recording = False
    
    def audio_callback(indata, frames, time_info, status):
        nonlocal recorded_frames, silent_frames, is_recording
        
        volume_norm = np.linalg.norm(indata) * 10
        if volume_norm > SILENCE_THRESHOLD:
            if not is_recording:
                 is_recording = True
            silent_frames = 0
        elif is_recording:
            silent_frames += 1
            
        if is_recording:
             recorded_frames.append(indata.copy())
             
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback):
        # Wait until recording starts and then stops due to silence
        while True:
            time.sleep(0.1)
            # 1 frame = usually 1024 samples. 
            # sounddevice default blocksize varies. We use time to measure silence roughly.
            # A simple heuristic: if we have recorded something and it's been silent for SILENCE_DURATION
            # We exit
            if is_recording and (silent_frames * 0.1) > SILENCE_DURATION: # Roughly assuming 0.1s sleep aligns with frames
                break
                
    if not recorded_frames:
         return None
         
    # Save to WAV
    audio_data = np.concatenate(recorded_frames, axis=0)
    with wave.open(str(output_path), 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2) # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
    return str(output_path)
