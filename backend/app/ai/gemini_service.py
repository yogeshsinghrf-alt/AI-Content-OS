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
            model="gemini-3.6-flash",
            contents=prompt,
        )

        time.sleep(2)

        return response.text


    except Exception as error:
        print(
            "\n========== GEMINI ERROR =========="
        )
        print(
            "Error type:",
            type(error).__name__,
        )
        print(
            "Error:",
            str(error),
        )
        print(
            "==================================\n"
        )

        error_text = str(
            error
        ).lower()

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
            print(
                "\n========== GEMINI QUOTA ERROR =========="
            )
            print(
                str(error)
            )
            print(
                "========================================\n"
            )

            raise AIQuotaError(
                f"Gemini quota error: {str(error)}"
            ) from error

        raise AIServiceError(
            f"Gemini generation failed: {str(error)}"
        ) from error