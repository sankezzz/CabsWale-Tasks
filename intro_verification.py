import os
from prep import genai,MODEL
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"

from google.cloud import speech
import io

def transcribe_audio(audio_path):
    client = speech.SpeechClient()

    with io.open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="hi-IN",
        enable_automatic_punctuation=True,
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        transcript=result.alternatives[0].transcript
    return transcript

# Example usage

audio_trans=transcribe_audio("video/audio2.mp3")
from prep import genai,MODEL

gen_model=genai.GenerativeModel(MODEL)

prompt=f'''
i will give you a hindi transcript you should tell wether the person speaking in this has mentioned his name or not 
and check the sentiment and tone of the person is he positive and confident 
 {audio_trans}
if the person has mentioned his name then we will return a json format 
{{
  "name":boolean
  "sentiment":"positive"/"negetive"
}}
strictly give json format hata only nothing other than that 

'''

response=gen_model.generate_content(prompt)

print(response)
print(response.text)
