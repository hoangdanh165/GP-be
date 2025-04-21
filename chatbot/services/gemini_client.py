import os
from pathlib import Path
from google import genai
from dotenv import load_dotenv

dotenv_path = Path(os.getcwd() + "/config.env")
load_dotenv(dotenv_path=dotenv_path)

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("GEMINI_MODEL")

# Client initialization
client = genai.Client(api_key=API_KEY)
model_name = MODEL
