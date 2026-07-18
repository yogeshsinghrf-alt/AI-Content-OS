from fastapi import APIRouter
from app.ai.gemini_service import generate_summary

router = APIRouter()


@router.get("/x-post")
def x_post():
    text = """
    NVIDIA released enterprise AI fine tuning tools
    to simplify AI deployment.
    """

    prompt = f"""
    Write one high-quality X/Twitter post.

    News:
    {text}

    Requirements:
    - Maximum 260 characters
    - Clear hook
    - Professional tone
    - Add 2 hashtags
    """

    result = generate_summary(prompt)

    return {
        "x_post": result
    }


@router.get("/instagram-caption")
def instagram_caption():
    text = """
    NVIDIA released enterprise AI fine tuning tools
    to simplify AI deployment.
    """

    prompt = f"""
    Write one Instagram caption.

    News:
    {text}

    Requirements:
    - Engaging opening line
    - Simple language
    - 80 words maximum
    - Add 5 relevant hashtags
    """

    result = generate_summary(prompt)

    return {
        "instagram_caption": result
    }