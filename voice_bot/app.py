from flask import Flask,render_template
import json
from google.cloud import speech, dialogflow_v2 as dialogflow, texttospeech
import io
import os
from record_audio import record_audio
import playsound
from prep import genai,MODEL
import time
import re
from datetime import datetime


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"
gen_model=genai.GenerativeModel(MODEL)
app = Flask(__name__)

year = datetime.now().year
year = str(year)

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


PROJECT_ID = "cabswale-test"
LANGUAGE_CODE = "en-US"
buffer_memory=[""]
buffer_memory_ai_response=[]


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/record_audio")
def run_bot():
    # Step 1: Record voice
    audio_file = record_audio(duration=10)

    # Step 2: Convert voice to text (STT)
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
    print(buffer_memory)

    prompt=f'''
You are a friendly, female cab travel assistant from कैबस्वाले having a conversation with the user.
The user speaks in Hindi, Panjabi, Haryanvi, Marathi, or English. Your job is:
- Continue the natural conversation in the same language and help them get the best cab from us.
- The user is using our कैबस्वाले app for outstation travel. Encourage them to book with us.

#MANDATORY FIELDS YOU NEED TO GET FROM THE USER
- Detect the source city (from where the user wants to travel).just ask the city nothing more --- if the user giving some village / town name ask the nearest city or in which ity is that place.
- Detect the destination city (where they want to go) just ask the city nothing more --- if the user giving some village / town name ask the nearest city or in which ity is that place.
- Detect the number of passengers.
- Ask the exact date when the person wants to leave. Consider the current year = {year}.
- The return/end date is not compulsory, but ask politely.
- Make the conversation friendly and keep it engaging dont end on a blank note.
- You need to keep the conversation going until you get all the above fields.
- Once all fields are collected, thank the user and end with a friendly company note.
- dont answer any thing other than this context

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
  "destination_city": "<destination city name or null>",
  "start_date":"<the day on which the journy will begin>",
  "end date":"<The day on which journy will end>"
}}


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
    print(spoken_part)
    print("####FINAL JSON OUTPUT######",json_output)


    # Step 4: Convert reply to speech (TTS)
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=spoken_part)
    voice = texttospeech.VoiceSelectionParams(language_code='hi-IN', name="hi-IN-Chirp3-HD-Aoede", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

    tts_response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open("response.wav", "wb") as out:
        out.write(tts_response.audio_content)

    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load('response.wav')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit() 

    

    return "Conversation complete!"


if __name__ == "__main__":
    app.run(debug=True)
