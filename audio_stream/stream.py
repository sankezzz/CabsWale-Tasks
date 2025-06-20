from google.cloud import speech,texttospeech
import pyaudio
import os 
from prep import genai,MODEL
import pygame
import re
import json 
import datetime
import time

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"
generative_model=genai.GenerativeModel(MODEL)

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

def generate_audio_chunks():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("Listening...")
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow = False)
            yield data
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

import sys
def listen_print_loop(responses):
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        if result.is_final:
            sys.stdout.write(f"\rFinal Transcript: {transcript}\n")
            sys.stdout.flush()
            return transcript
        else:
            sys.stdout.write(f"\rPartial: {transcript} ")
            sys.stdout.flush()

def get_STT():
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="hi-IN",
        alternative_language_codes=["en-IN"],
        profanity_filter=False
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )

    audio_generator = generate_audio_chunks()
    requests = (speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in audio_generator)

    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests
    )

    transcript = listen_print_loop(responses)

    return transcript





def get_gemini_results(transcript,buffer1,buffer2):
    date=datetime.date.today()
    prompt=f'''
"""
You are a smart, helpful, and professional **female travel assistant from CabsWale**.

You assist Hindi-speaking users with **intercity cab bookings only** — and strictly stay on topic.
-dont greet again and again and dont repet the same sentences

Your speaking style:
- Conversational and easy-to-understand Hindi
- Not too formal, not too casual — friendly and approachable
- Like a helpful and trustworthy person talking to a layman user
- Professional but not robotic

You are interacting with the user in a **voice-based chat** and can remember past interactions.

---

Conversation so far:
User:
{buffer1}

 You (CabsWale Assistant):
{buffer2}

---

 Your goal is to extract the following booking details:
- Source city (where the journey starts)
- Destination city (where the user wants to go)
- One-way or two-way trip
- Leaving date
- Return date (only if it’s a two-way trip)
- Number of passengers

---

 Important Instructions:
- **Only discuss cab booking** — ignore or redirect unrelated queries
- **Ask for missing details politely in Hindi**
- When all details are collected, generate a **final confirmation message in Hindi**, summarizing the trip
- Always reply in short, clear, and polite **Hindi**
- Your tone should sound like a trusted, helpful female assistant from CabsWale

---

 Example Response Tone:
- "जी हाँ, बिलकुल! कहाँ से चलना है आपको?"
- "ठीक है, जाने की तारीख बता दें ताकि मैं आगे प्रोसेस कर सकूँ।"
- "आपने कहा दो लोग हैं और दिल्ली से जयपुर जाना है। क्या ये यात्रा एक तरफ़ा होगी या वापसी भी है?"
- "तो मैं आपकी बुकिंग की जानकारी कन्फर्म कर रही हूँ..."

---





'''

    results=generative_model.generate_content([prompt]+[transcript])    
    output=results.text
    return output

def get_TTS(output_text):
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=output_text)
    voice = texttospeech.VoiceSelectionParams(language_code='hi-IN', name="hi-IN-Chirp3-HD-Aoede", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)#hi-IN-Chirp3-HD-Aoede,hi-IN-Wavenet-A
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

    tts_response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    print("TTS working and speaking ")
    with open("response.wav", "wb") as out:
        out.write(tts_response.audio_content)

    pygame.mixer.init()
    pygame.mixer.music.load('response.wav')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit() 


if __name__ == "__main__":
    user_buffer=[]
    ai_buffer=[]
    while True:
        try:
            user_transcript = get_STT()
            user_buffer.append(user_transcript)
            print("getting gemini results")
            gemini_results=get_gemini_results(user_transcript,user_buffer,ai_buffer)
            get_TTS(output_text=gemini_results)
            time.sleep(2)
            print("you can speak again")
        except KeyboardInterrupt:
            print("\n Exiting...")
            break
        except Exception as e:
            print(f" Error: {e}")
