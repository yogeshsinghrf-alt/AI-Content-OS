import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing. Check backend/.env")

client = genai.Client(api_key=api_key)


def generate_summary(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        time.sleep(2)

        return response.text


    except Exception as e:
        return """
{
  "linkedin_option_1": "AI quota is temporarily exhausted. Please retry after a short break. This fallback keeps the dashboard working for demo purposes. #AI #Automation #Content",
  "linkedin_option_2": "Even when AI APIs hit rate limits, a well-designed system should fail gracefully. AI Content OS now demonstrates error handling and fallback behavior. #AIAutomation #SoftwareEngineering #Gemini",
  "x_option_1": "Gemini quota reached temporarily. Please retry shortly. #AI #Automation",
  "x_option_2": "Good AI systems need graceful fallbacks, not crashes. #SoftwareEngineering #AI",
  "instagram_option_1": "AI quota temporarily reached. The system is still running with fallback content. #AI #Automation #Tech #Content #Gemini",
  "instagram_option_2": "Building reliable AI apps means handling API limits gracefully. #AI #Developer #Automation #SaaS #Content",
  "hero_image_prompt": "Warm cream modern SaaS dashboard visual, abstract AI content engine, elegant cards, soft shadows, no people photos, premium European style"
}
"""