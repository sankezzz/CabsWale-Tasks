from flask import Flask, render_template,json
from google.cloud import speech
import io
import os
from record_audio import record_audio
import playsound
from prep import genai, MODEL
import pygame
import requests
import re

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"
gen_model = genai.GenerativeModel(MODEL)
app = Flask(__name__)
PROJECT_ID = "cabswale-test"
LANGUAGE_CODE = "en-US"
ELEVEN_API_KEY = ''
ELEVEN_VOICE_ID = ''
buffer_memory = []
buffer_memory_ai_response = []


def extract_json_from_response(full_reply):

    match = re.search(r'\{.*\}', full_reply, re.DOTALL)
    if match:
        json_str = match.group(0).strip()

        try:
            parsed = json.loads(json_str)
            print(" Extracted JSON:", parsed)
            return parsed
        except json.JSONDecodeError as e:
            print(" JSON Decode Error:", e)
            return {}
    else:
        print(" No JSON found.")
        return {}


def elevenlabs_tts(text, api_key, voice_id=ELEVEN_VOICE_ID, output_file="response.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v1",  # For Hindi and others
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f" ElevenLabs TTS saved to {output_file}")
            return output_file
        else:
            print(f" Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f" Request failed: {e}")
        return None

@app.route("/")
def main():
    return render_template("index.html")


@app.route("/record_audio")
def run_bot():
    audio_file = record_audio(duration=5)

    stt_client = speech.SpeechClient()
    with io.open(audio_file, "rb") as audio:
        content = audio.read()

    audio_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        language_code="hi-IN",
        sample_rate_hertz=16000,
    )

    audio = speech.RecognitionAudio(content=content)
    response = stt_client.recognize(config=audio_config, audio=audio)

    if not response.results:
        return "No speech detected.", 400

    text_input = response.results[0].alternatives[0].transcript.strip()
    if not text_input:
        return "Speech was empty.", 400

    buffer_memory.append(text_input)
    print("You said:", text_input)

    source_city,destination_city=[],[]
    
    print(buffer_memory)
    prompt = f'''
        You are a friendly, female cab travel assistant from 
कैबस्वाले having a conversation with the user.
        The user speaks in Hindi, Marathi, or English. Your job is:
        - Continue the natural conversation in the same language and help them plan their trip.
        - Detect the source city (from where the user wants to travel).
        - Detect the destination city (where they want to go).
        -when you have detected both the source and destination just try to end the conversation
        -the user is on our cabs app for outstation travel and we need to make the user use our service

    #Context of the before chat 
    User said: "{text_input}"
    Previous conversation: "{' '.join(buffer_memory)}"
    Your previous replies: "{' '.join(buffer_memory_ai_response)}"

IMPORTANT:
- First, reply naturally as if you're talking to the user. Keep it friendly and under 20 words.
- At the end, on a **new line**, include this hidden JSON block for backend use only.
Format your full output like this:
<Your natural reply>

###JSON
{{
  "source_city": "<source city name or null>",
  "destination_city": "<destination city name or null>"
}}

User said: "{text_input}"
Previous conversation: "{' '.join(buffer_memory)}"
Your previous replies: "{' '.join(buffer_memory_ai_response)}"

        '''


    output = gen_model.generate_content(prompt)
    reply = output.text.strip()

    if "###JSON" in reply:
        spoken_part, _ = reply.split("###JSON", 1)
        spoken_part = spoken_part.strip()
    else:
        spoken_part = reply.strip()

    json_output = extract_json_from_response(reply)


    buffer_memory_ai_response.append(spoken_part)

    # Debug prints
    print("Spoken:", spoken_part)

    print("Full JSON:", json_output)
    print("AI Memory:", buffer_memory_ai_response)

    print("####FINAL JSON OUTPUT######",json_output)


    # Step 4: TTS
    tts_path = elevenlabs_tts(spoken_part, api_key='')
    if not tts_path:
        return "TTS failed", 500

# Play using pygame
    pygame.mixer.init()
    pygame.mixer.music.load(tts_path)
    pygame.mixer.music.play()
    


    # Wait until done
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit()
        

    return "conversation done "



if __name__ == "__main__":
    app.run(debug=True)
