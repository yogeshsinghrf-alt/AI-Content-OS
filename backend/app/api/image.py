import os

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
            "Square executive business editorial photograph "
            "with a sophisticated professional composition."
        ),
        "instagram": (
            "Portrait editorial photograph with strong visual "
            "storytelling and premium magazine styling."
        ),
        "x": (
            "Wide editorial photograph with one strong focal "
            "subject and generous negative space."
        ),
        "carousel": (
            "Square editorial photograph with a bold physical "
            "subject and cinematic composition."
        ),
        "infographic": (
            "Portrait editorial background photograph with "
            "structured visual balance and clean negative space."
        ),
        "quote": (
            "Minimal square editorial photograph with elegant "
            "negative space."
        ),
        "hero": (
            "Premium business editorial hero photograph with "
            "a cinematic professional composition."
        ),
    }.get(
        platform,
        "Premium business editorial photograph.",
    )

    # ---------------------------------------------
    # Clean software / UI terminology from subject
    # ---------------------------------------------

    clean_prompt = prompt

    blocked_phrases = [
        "saas dashboard",
        "saas",
        "ai content engine",
        "content engine",
        "user interface",
        "web page",
        "dashboard",
        "interface",
        "website",
        "browser",
        "screen",
        "headline",
        "caption",
        "title",
        "logo",
        "software",
        "app",
        "cards",
    ]

    for phrase in blocked_phrases:
        clean_prompt = clean_prompt.replace(
            phrase,
            "",
        )
        clean_prompt = clean_prompt.replace(
            phrase.title(),
            "",
        )
        clean_prompt = clean_prompt.replace(
            phrase.upper(),
            "",
        )

    clean_prompt = " ".join(
        clean_prompt.split()
    )

    if len(clean_prompt) < 15:
        clean_prompt = (
            "advanced artificial intelligence infrastructure "
            "and modern enterprise technology"
        )

    # ---------------------------------------------
    # Primary image prompt
    # ---------------------------------------------

    primary_prompt = f"""
{platform_instruction}

Editorial photograph inspired by this subject:

{clean_prompt}

Create a real-world physical interpretation of the subject.

Use authentic physical environments and objects appropriate
to the story, such as computing infrastructure, data centers,
semiconductor hardware, telecommunications equipment,
industrial engineering, energy infrastructure, architecture,
research environments or enterprise technology facilities.

High-end international business editorial photography.
Photorealistic.
Sophisticated European and American publication aesthetic.
Natural cinematic lighting.
Warm neutral color palette.
Realistic materials.
Architectural depth.
Strong photographic focal point.
Clean composition.
Generous negative space.
Subtle depth of field.
Professional commercial photography.
""".strip()

    # ---------------------------------------------
    # Neutral fallback prompt
    # ---------------------------------------------

    fallback_prompt = f"""
{platform_instruction}

High-end editorial photograph of modern technology
infrastructure inside a sophisticated architectural environment.

Real physical equipment.
Premium industrial design.
Warm natural lighting.
Neutral sophisticated colors.
Architectural photography.
Photorealistic materials.
Cinematic depth.
Clean uncluttered composition.
One strong visual subject.
Generous negative space.
Professional international business photography.
""".strip()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    def request_image(image_prompt: str):
        payload = {
            "prompt": image_prompt,
            "model": "zimage",
            "n": 1,
            "size": f"{width}x{height}",
            "response_format": "b64_json",
            "safe": True,
        }

        response = requests.post(
            "https://gen.pollinations.ai/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=180,
        )

        if response.status_code != 200:
            return None, (
                f"{response.status_code} "
                f"{response.text[:700]}"
            )

        try:
            result = response.json()
        except ValueError:
            return None, "Provider returned invalid JSON."

        data = result.get("data", [])

        if not data:
            return None, "Provider returned no image data."

        b64_image = data[0].get("b64_json")

        if not b64_image:
            return None, "Provider returned no base64 image."

        return b64_image, None

    try:
        # First attempt
        b64_image, first_error = request_image(
            primary_prompt
        )

        used_prompt = primary_prompt
        fallback_used = False

        # Second attempt if first request failed
        if not b64_image:
            b64_image, second_error = request_image(
                fallback_prompt
            )

            used_prompt = fallback_prompt
            fallback_used = True

            if not b64_image:
                raise HTTPException(
                    status_code=502,
                    detail=(
                        "Pollinations image generation failed. "
                        f"First attempt: {first_error}. "
                        f"Fallback attempt: {second_error}."
                    ),
                )

        image_url = (
            "data:image/png;base64,"
            f"{b64_image}"
        )

        return {
            "status": "success",
            "image_url": image_url,
            "prompt": used_prompt,
            "platform": platform,
            "width": width,
            "height": height,
            "model": "pollinations-zimage",
            "fallback_used": fallback_used,
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