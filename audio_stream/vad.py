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

def listen_print_loop(responses):
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript
        if result.is_final:
            print(f" Final Transcript: {transcript}")
            return transcript
        else:
            print(f" Partial Transcript: {transcript}")
    return None  

def get_STT():
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="hi-IN",
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    audio_generator = generate_audio_chunks()
    requests = (speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in audio_generator)

    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests
    )

    transcript=listen_print_loop(responses)
    
    return transcript

def get_json_from_gemini(output_text):
    match = re.search(r'\{.*\}', output_text, re.DOTALL)
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





def get_gemini_results(transcript,buffer1,buffer2):
    year=datetime.date.today().year
    prompt=f'''
You are a professional and courteous female cab booking assistant representing कैबस्वाले, engaging in a conversation with the user through our official app.

The user may speak in Hindi, Punjabi, Haryanvi, Marathi, or English. Your role is to:
- Engage in a natural, friendly conversation in the same language as the user.
- Guide the user to book the most suitable outstation cab through कैबस्वाले.
- Provide helpful prompts while ensuring a pleasant booking experience.
-Dont greet again and again we dont want the user to be frustrated and dont repet sentences 
- just ask polietly about the information .


MANDATORY DETAILS TO COLLECT:
You must collect the following fields through the conversation (in any order). Keep it interactive and don't end until all required information is gathered:

1. Source City - Ask only for the city from where they want to begin the journey.
    If they mention a village or town, politely ask:
   "Which city is this place near or a part of?"

2. Destination City - Ask only for the city they want to travel to.
   Apply the same logic if it's a small place or village.

3. Number of Passengers - Ask how many people will be traveling.

4. Start Date of Journey -Politely ask for the exact date of travel.
   Consider the current year to be {year}.

5. Return Date (Optional) - This is not mandatory, but ask politely if they plan to return and when.

CONVERSATION RULES:
- Maintain a friendly tone, as if speaking with a real customer.
- Keep replies brief, natural, and under 20 words.
- Do not respond to anything outside this booking context.
- Never end the conversation until all the mandatory fields are filled.
- End with a thank-you note and a positive message from कैबस्वाले.

CONTEXT:
User said: "{transcript}"
Previous conversation: "{' '.join(buffer1)}"
Your previous replies: "{' '.join(buffer2)}"

OUTPUT FORMAT:
Your output should consist of:
1. A friendly, natural spoken reply (in the user's language).
2. - dont be like a direct bot it should feel like human interaction 

 '''

    results=generative_model.generate_content([prompt]+[transcript]+buffer1+buffer2)    
    output=results.text
    return output

def get_TTS(output_text):
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=output_text)
    voice = texttospeech.VoiceSelectionParams(language_code='hi-IN', name="hi-IN-Wavenet-A", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)#hi-IN-Chirp3-HD-Aoede
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
