from fastapi import APIRouter
from app.ai.gemini_service import generate_summary

router = APIRouter()


@router.get("/generate")
def generate_image(prompt: str):
    enhanced_prompt = f"""
    Create a premium editorial image prompt for this idea:

    {prompt}

    Style:
    warm cream background,
    elegant European/US editorial design,
    soft lighting,
    minimal layout,
    no people photos,
    no neon cyberpunk,
    no robots,
    suitable for LinkedIn and Instagram.
    """

    final_prompt = generate_summary(enhanced_prompt)

    return {
        "image_url": "https://picsum.photos/1200/800?random=2",
        "prompt": final_prompt
    }