import os 
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY=os.getenv('GEMINI_API_KEY')

MODEL=os.getenv('MODEL_GEMINI_2_FLASH')

genai.configure(api_key=API_KEY)
sk_3a0ffd2e6c10ec643257a857deea8199cd225c219858848a