import sounddevice as sd
from scipy.io.wavfile import write
import uuid

def record_audio(duration=5, fs=16000):
    filename = f"recorded_{uuid.uuid4().hex[:6]}.wav"
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    write(filename, fs, audio)
    print("Saved:", filename)
    return filename
