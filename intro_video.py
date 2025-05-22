import os
import assemblyai as aai
from prep import MODEL, genai

# Init Gemini model
gen_model = genai.GenerativeModel(MODEL)

# Set AssemblyAI API key
aai.settings.api_key = ""

# Audio file path
audio_file = "video/audio.mp3"

# Transcription
def transcribe_audio(file_path):
    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)
    transcript = aai.Transcriber(config=config).transcribe(file_path)

    if transcript.status == "error":
        raise RuntimeError(f"Transcription failed: {transcript.error}")

    print(" Transcription complete.")
    return transcript.text


# Transcript analysis using Gemini
def analyze_transcript(text):
    prompt = f"""
You are an assistant that analyzes personal introduction audio transcripts.

Given the transcript:
\"\"\"{text}\"\"\"
this transcript might be in hinglish and hindi and you need to understand it then only go through 
Return a JSON with:
- If the person mentioned their name
- If they mentioned any driving or professional experience
- Sentiment of tone (e.g., confident, hesitant, neutral)
- Any red flags mentioned (or null if none)

Respond strictly in this JSON format:
{{
  "name": true/false,
  "experience": true/false,
  "sentiment": "confident/hesitant/neutral",
  "red_flags": "string or null"
}}
"""

    response = gen_model.generate_content(prompt)
    print(" Analysis complete.")
    return response.text.strip()


# === Main flow ===
if __name__ == "__main__":
    transcript_text = transcribe_audio(audio_file)
    print("\n--- Transcript ---\n", transcript_text)

    analysis_json = analyze_transcript(transcript_text)
    print("\n--- Analysis JSON ---\n", analysis_json)
