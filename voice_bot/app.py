from flask import Flask,render_template
from google.cloud import speech, dialogflow_v2 as dialogflow, texttospeech
import io
import os
from record_audio import record_audio
import playsound
from prep import genai,MODEL

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"
gen_model=genai.GenerativeModel(MODEL)
app = Flask(__name__)

PROJECT_ID = "cabswale-test"
LANGUAGE_CODE = "en-US"
buffer_memory=[""]


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/record_audio")
def run_bot():
    # Step 1: Record voice
    audio_file = record_audio(duration=5)

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

    prompt='''you are a chatbot and you need to give reply to the user in a really good manner and your reply will be converted to speech so talk you need to consider in english keep the output short and less within 10 words you will also given buffer memory that what the user has said before for the context of the user as {buffer_memory} only give output as you are speaking to person '''

    output=gen_model.generate_content([prompt]+[text_input]+buffer_memory)
    reply=output.text
    print("Gemini Reply:",reply)

    # Step 4: Convert reply to speech (TTS)
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=reply)
    voice = texttospeech.VoiceSelectionParams(language_code=LANGUAGE_CODE, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

    tts_response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open("response.wav", "wb") as out:
        out.write(tts_response.audio_content)

    # Step 5: Play the audio
    playsound.playsound("response.wav") 

    return "Conversation complete!"


if __name__ == "__main__":
    app.run(debug=True)
