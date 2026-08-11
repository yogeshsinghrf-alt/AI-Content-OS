import base64
import os
import random
from urllib.parse import quote

import requests
from fastapi import APIRouter, HTTPException


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
            "Premium LinkedIn business editorial visual. "
            "Credible, sophisticated and suitable for "
            "executive thought leadership."
        ),
        "instagram": (
            "Premium Instagram portrait editorial visual. "
            "Visually expressive and magazine-inspired."
        ),
        "x": (
            "Premium wide editorial visual for X. "
            "Strong focal idea and generous negative space."
        ),
        "carousel": (
            "Premium square social carousel cover. "
            "Bold editorial composition and clean hierarchy."
        ),
        "infographic": (
            "Premium portrait infographic-style visual. "
            "Structured and professional."
        ),
        "quote": (
            "Premium square quote-card background. "
            "Minimal, elegant and spacious."
        ),
        "hero": (
            "Premium business-magazine hero visual. "
            "Sophisticated European and American editorial style."
        ),
    }.get(
        platform,
        "Premium editorial business visual.",
    )

    final_prompt = f"""
{prompt}

{platform_instruction}

Create a high-end editorial image directly related to the subject.

Style requirements:
- modern European / US business-magazine aesthetic
- sophisticated editorial photography or illustration
- professional composition
- warm light-neutral palette where appropriate
- realistic materials and lighting
- strong focal point
- elegant negative space
- visually distinctive, not generic stock imagery
- no written text
- no logos
- no watermark
- no fake interface elements
- no generic AI brain imagery
- no humanoid robots unless directly relevant
- no neon cyberpunk aesthetic
""".strip()

    seed = random.randint(
        1,
        2_147_483_647,
    )

    encoded_prompt = quote(
        final_prompt,
        safe="",
    )

    provider_url = (
        f"https://gen.pollinations.ai/image/"
        f"{encoded_prompt}"
        f"?model=zimage"
        f"&width={width}"
        f"&height={height}"
        f"&seed={seed}"
        f"&safe=true"
        f"&key={api_key}"
    )

    try:
        response = requests.get(
            provider_url,
            timeout=120,
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Pollinations image generation failed: "
                    f"{response.status_code} "
                    f"{response.text[:500]}"
                ),
            )

        content_type = response.headers.get(
            "content-type",
            "image/jpeg",
        )

        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=502,
                detail=(
                    "Pollinations returned a non-image response."
                ),
            )

        encoded_image = base64.b64encode(
            response.content
        ).decode("utf-8")

        image_url = (
            f"data:{content_type};base64,"
            f"{encoded_image}"
        )

        return {
            "status": "success",
            "image_url": image_url,
            "prompt": final_prompt,
            "platform": platform,
            "width": width,
            "height": height,
            "seed": seed,
            "model": "pollinations-zimage",
        }

    except HTTPException:
        raise

    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not reach Pollinations: "
                f"{str(error)}"
            ),
        )