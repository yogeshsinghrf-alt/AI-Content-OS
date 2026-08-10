import base64
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from google import genai
from google.genai import types

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


PLATFORM_ASPECT_RATIOS = {
    "linkedin": "1:1",
    "instagram": "4:5",
    "x": "16:9",
    "carousel": "1:1",
    "infographic": "4:5",
    "quote": "1:1",
    "hero": "3:2",
}


GENERATED_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
    / "generated_images"
)


@router.get("/generate")
def generate_image(
    prompt: str,
    platform: str = "hero",
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing.",
        )

    width, height = PLATFORM_SIZES.get(
        platform,
        PLATFORM_SIZES["hero"],
    )

    aspect_ratio = PLATFORM_ASPECT_RATIOS.get(
        platform,
        "1:1",
    )

    platform_instruction = {
        "linkedin": (
            "Premium LinkedIn business editorial visual. "
            "Credible, sophisticated and appropriate for "
            "executive thought leadership."
        ),

        "instagram": (
            "Premium Instagram editorial visual. "
            "Portrait-first, visually expressive, modern "
            "magazine art direction."
        ),

        "x": (
            "Premium wide editorial visual for X. "
            "One strong focal idea, concise composition "
            "and generous negative space."
        ),

        "carousel": (
            "Premium social carousel cover. "
            "Square editorial composition with a strong "
            "visual concept and clean hierarchy."
        ),

        "infographic": (
            "Premium infographic-style editorial visual. "
            "Portrait format, structured composition, "
            "professional data-inspired visual language."
        ),

        "quote": (
            "Premium quote-card background. "
            "Square, minimal, elegant and spacious."
        ),

        "hero": (
            "Premium business-magazine hero visual. "
            "Sophisticated European and American editorial style."
        ),
    }.get(
        platform,
        "Premium editorial business visual.",
    )

    enhanced_prompt = f"""
Create a high-end editorial image.

SUBJECT:
{prompt}

PLATFORM DIRECTION:
{platform_instruction}

ART DIRECTION:

- directly represent the actual subject
- modern European / US business-magazine aesthetic
- sophisticated editorial photography or illustration
- premium composition
- professional visual storytelling
- warm light neutral palette where appropriate
- strong focal point
- elegant use of negative space
- realistic materials and lighting
- visually distinctive, not generic stock imagery

AVOID:

- written text
- logos
- watermarks
- fake UI
- generic AI brains
- glowing humanoid robots
- neon cyberpunk aesthetics
- people staring directly at camera
- unnecessary futuristic clichés

The final image should look suitable for a premium
business publication and professional social-media campaign.
"""

    try:
        # Optional prompt refinement using the text model
        final_prompt = generate_summary(
            f"""
Rewrite the following as one concise,
professional image-generation prompt.

Return only the image prompt.

{enhanced_prompt}
"""
        ).strip()

        if not final_prompt:
            final_prompt = enhanced_prompt

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-image",
            contents=final_prompt,
            config=types.GenerateContentConfig(
                response_modalities=[
                    "IMAGE",
                ],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                ),
            ),
        )

        image_bytes = None
        mime_type = "image/png"

        for candidate in response.candidates or []:
            if not candidate.content:
                continue

            for part in candidate.content.parts or []:
                if part.inline_data:
                    image_bytes = (
                        part.inline_data.data
                    )

                    if part.inline_data.mime_type:
                        mime_type = (
                            part.inline_data.mime_type
                        )

                    break

            if image_bytes:
                break

        if not image_bytes:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Gemini returned no image data."
                ),
            )

        GENERATED_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        extension = (
            ".jpg"
            if "jpeg" in mime_type.lower()
            else ".png"
        )

        filename = (
            f"{platform}_"
            f"{os.urandom(6).hex()}"
            f"{extension}"
        )

        file_path = (
            GENERATED_DIR
            / filename
        )

        file_path.write_bytes(
            image_bytes
        )

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_url = (
            f"data:{mime_type};base64,"
            f"{encoded_image}"
        )

        return {
            "status": "success",
            "image_url": image_url,
            "prompt": final_prompt,
            "platform": platform,
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "model": "gemini-3.1-flash-image",
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Gemini image generation failed: "
                f"{str(error)}"
            ),
        )