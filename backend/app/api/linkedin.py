from fastapi import APIRouter
from app.ai.gemini_service import generate_summary

router = APIRouter()


@router.get("/post")
def linkedin_post():
    text = """
    NVIDIA released enterprise AI fine tuning tools
    to simplify AI deployment.
    """

    prompt = f"""
    Write a professional LinkedIn post.

    News:
    {text}

    Requirements:
    - Professional tone
    - 120 words maximum
    - Add 3 hashtags
    """

    result = generate_summary(prompt)

    return {
        "linkedin_post": result
    }