from flask import Flask
from google.cloud import speech, dialogflow_v2 as dialogflow, texttospeech
import io
import os
from record_audio import record_audio
import playsound

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"

app = Flask(__name__)

PROJECT_ID = "cabswale-test"
LANGUAGE_CODE = "en-US"

@app.route("/")
def run_bot():
    # Step 1: Record voice
    audio_file = record_audio(duration=5)

    # Step 2: Convert voice to text (STT)
    stt_client = speech.SpeechClient()
    with io.open(audio_file, "rb") as audio:
        content = audio.read()

    audio_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        language_code=LANGUAGE_CODE,
        sample_rate_hertz=16000,
    )

    audio = speech.RecognitionAudio(content=content)
    response = stt_client.recognize(config=audio_config, audio=audio)
    if not response.results:
        return "No speech detected.", 400

    text_input = response.results[0].alternatives[0].transcript.strip()
    if not text_input:
        return "Speech was empty.", 400

    print("You said:", text_input)

    # Step 3: Send text to Dialogflow
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(PROJECT_ID, "123456789")
    text = dialogflow.TextInput(text=text_input, language_code=LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text)

    dialogflow_response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    reply = dialogflow_response.query_result.fulfillment_text
    if not reply.strip():
        return "Dialogflow response was empty.", 400
    print("Bot:", reply)

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
