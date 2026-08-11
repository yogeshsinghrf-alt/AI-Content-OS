import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()


class AIQuotaError(Exception):
    """Raised when Gemini quota or rate limits are unavailable."""
    pass


class AIServiceError(Exception):
    """Raised when Gemini fails for another reason."""
    pass


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check backend/.env"
    )


client = genai.Client(
    api_key=api_key
)


def generate_summary(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        time.sleep(2)

        if not response.text:
            raise AIServiceError(
                "Gemini returned an empty response."
            )

        return response.text

    except AIServiceError:
        raise

    except Exception as error:
        error_text = str(error).lower()

        quota_indicators = [
            "resource_exhausted",
            "resource exhausted",
            "quota",
            "429",
            "rate limit",
            "rate_limit",
            "prepayment credits",
            "credits are depleted",
        ]

        if any(
            indicator in error_text
            for indicator in quota_indicators
        ):
            raise AIQuotaError(
                "AI generation quota is temporarily unavailable."
            ) from error

        raise AIServiceError(
            f"Gemini generation failed: {str(error)}"
        ) from error