import os
import random
from urllib.parse import quote

from fastapi import APIRouter, HTTPException

from app.ai.gemini_service import generate_summary


router = APIRouter()


PLATFORM_SIZES = {
    "linkedin": (1200, 1200),
    "instagram": (1080, 1350),
    "x": (1600, 900),
    "carousel": (1080, 1080),
    "infographic": (1080, 1350),
    "quote": (1080, 1080),
    "hero": (1200, 800),
}


@router.get("/generate")
def generate_image(
    prompt: str,
    platform: str = "hero",
):
    api_key = os.getenv("POLLINATIONS_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="POLLINATIONS_API_KEY is missing.",
        )

    width, height = PLATFORM_SIZES.get(
        platform,
        PLATFORM_SIZES["hero"],
    )

    platform_instruction = {
        "linkedin": (
            "Create a premium square LinkedIn business editorial image. "
            "Professional, credible, elegant, and suitable for executive audiences."
        ),
        "instagram": (
            "Create a premium portrait Instagram editorial image. "
            "Cinematic, visually bold, warm, and magazine-inspired."
        ),
        "x": (
            "Create a premium wide image for X. "
            "Minimal, modern, high-contrast, with clean negative space."
        ),
        "carousel": (
            "Create a premium square carousel-cover image. "
            "Bold editorial composition with a strong focal point."
        ),
        "infographic": (
            "Create a portrait infographic background. "
            "Structured, minimal, professional, and data-oriented."
        ),
        "quote": (
            "Create a refined square quote-card background. "
            "Minimal, elegant, and with generous negative space."
        ),
        "hero": (
            "Create a premium editorial hero image. "
            "Elegant European and American business-magazine style."
        ),
    }.get(platform, "")

    enhanced_prompt = f"""
Create one high-end editorial image-generation prompt.

Topic:
{prompt}

Platform direction:
{platform_instruction}

Requirements:
- modern European business-magazine style
- premium and minimal
- elegant warm palette
- soft cinematic lighting
- no written text
- no watermark
- no logos
- no people looking directly at the camera
- no robots unless the topic is robotics
- high-end editorial illustration or photography
- strong professional composition

Return only the final image prompt.
"""

    final_prompt = generate_summary(enhanced_prompt).strip()

    if not final_prompt:
        raise HTTPException(
            status_code=500,
            detail="Could not generate an image prompt.",
        )

    seed = random.randint(1, 2_147_483_647)
    encoded_prompt = quote(final_prompt, safe="")

    image_url = (
        f"https://gen.pollinations.ai/image/{encoded_prompt}"
        f"?model=zimage"
        f"&width={width}"
        f"&height={height}"
        f"&seed={seed}"
        f"&safe=true"
        f"&key={api_key}"
    )

    return {
        "image_url": image_url,
        "prompt": final_prompt,
        "platform": platform,
        "width": width,
        "height": height,
        "seed": seed,
    }