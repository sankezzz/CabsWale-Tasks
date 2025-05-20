import os
from openai import OpenAI  # new import style
from prep import MODEL, genai
import json
import re

gen_model = genai.GenerativeModel(MODEL)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Or set your key here directly

# === Step 2: Transcribe audio using Whisper (new SDK usage) ===
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )
    print("Transcription done.")
    return transcript.text

# === Step 3: Analyze transcript using GPT-4 ===
def analyze_transcript(transcript_text):
    prompt = f"""
Analyze the following personal introduction:

"{transcript_text}"

Check and return in JSON format:
1. Did the speaker mention their name?
2. Did they describe their professional driving experience?
3. Is the tone confident or hesitant?
4. What is the overall sentiment?
5. Are there any red flags?
"""
    response = gen_model.generate_content(prompt)

    analysis = response["choices"][0]["message"]["content"]
    print("Analysis Complete.")
    return analysis

# === Main flow ===
if __name__ == "__main__":
    audio_path = "video/audio.mp3"

    transcript = transcribe_audio(audio_path)
    print("\n--- Transcript ---\n", transcript)

    analysis = analyze_transcript(transcript)
    print("\n--- Analysis ---\n", analysis)
