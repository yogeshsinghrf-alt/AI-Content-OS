import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

models = [
    "models/gemini-3.1-flash-tts-preview",
    "models/antigravity-preview-05-2026",
    "models/deep-research-preview-04-2026",
]

for model_name in models:
    print("\nTesting:", model_name)
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Write one short LinkedIn post about AI.")
        print("SUCCESS:")
        print(response.text)
        break
    except Exception as e:
        print("FAILED:")
        print(e)