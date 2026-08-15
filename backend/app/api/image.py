import base64
import os
import random
from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from app.services.package_service import update_package_asset


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


CLOUDFLARE_MODEL = "@cf/black-forest-labs/flux-1-schnell"

BACKEND_DIR = Path(__file__).resolve().parents[2]

GENERATED_DIR = (
    BACKEND_DIR
    / "generated_images"
)

GENERATED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def _clean_prompt_text(
    prompt: str,
) -> str:
    clean_prompt = str(
        prompt or ""
    )

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

    return clean_prompt


def _build_primary_prompt(
    prompt: str,
    platform: str,
) -> str:
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

    clean_prompt = _clean_prompt_text(
        prompt
    )

    return f"""
{platform_instruction}

Create a photorealistic editorial image inspired by:

{clean_prompt}

Interpret the story through real physical objects,
architecture, infrastructure, research environments,
telecommunications equipment, semiconductor hardware,
data centers, energy systems or modern enterprise
technology facilities.

The entire image must look like professional photography.

Natural cinematic lighting.
Premium business-magazine aesthetic.
Realistic materials.
Strong physical focal point.
Architectural depth.
Clean composition.
Generous negative space.
No visible text.
No letters.
No numbers.
No logos.
No signage.
No watermarks.
No software interface.
No dashboard.
No dialog box.
No popup.
No warning screen.
No error message.
No buttons.
No UI cards.
No visible monitor content.
""".strip()


def _normalize_provider_image(
    image_bytes: bytes,
    width: int,
    height: int,
) -> bytes:
    """
    Validate the provider image, center-crop it to the
    requested platform aspect ratio, resize it, and always
    return a PNG.
    """

    image = Image.open(
        BytesIO(image_bytes)
    ).convert("RGB")

    image = ImageOps.fit(
        image,
        (width, height),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
        optimize=True,
    )

    return buffer.getvalue()


def _create_local_safe_fallback(
    width: int,
    height: int,
    platform: str,
) -> bytes:
    """
    Guaranteed local fallback generated entirely by Pillow.
    It has no external provider dependency and cannot contain
    moderation screens or provider-generated text.
    """

    width = max(
        int(width),
        320,
    )

    height = max(
        int(height),
        320,
    )

    image = Image.new(
        "RGB",
        (width, height),
        (24, 30, 27),
    )

    draw = ImageDraw.Draw(
        image,
        "RGBA",
    )

    for step in range(18):
        inset = int(
            min(width, height)
            * 0.018
            * step
        )

        alpha = max(
            6,
            42 - step * 2,
        )

        draw.rounded_rectangle(
            (
                inset,
                inset,
                width - inset,
                height - inset,
            ),
            radius=max(
                12,
                int(
                    min(width, height)
                    * 0.045
                ),
            ),
            fill=(
                52 + step,
                61 + step,
                55 + step,
                alpha,
            ),
        )

    horizon_y = int(
        height * 0.62
    )

    draw.polygon(
        [
            (0, horizon_y),
            (width, horizon_y),
            (width, height),
            (0, height),
        ],
        fill=(47, 43, 38, 255),
    )

    draw.polygon(
        [
            (0, height),
            (
                int(width * 0.42),
                horizon_y,
            ),
            (
                int(width * 0.58),
                horizon_y,
            ),
            (width, height),
        ],
        fill=(66, 61, 54, 170),
    )

    rack_count = (
        5
        if platform in {
            "linkedin",
            "instagram",
            "carousel",
            "quote",
        }
        else 7
    )

    gap = width / (
        rack_count + 2
    )

    rack_width = int(
        gap * 0.58
    )

    rack_top = int(
        height * 0.20
    )

    rack_bottom = int(
        height * 0.70
    )

    for index in range(
        rack_count
    ):
        x = int(
            gap * (
                index + 1
            )
        )

        perspective_shift = int(
            (
                index
                - (
                    rack_count - 1
                )
                / 2
            )
            * gap
            * 0.05
        )

        left = (
            x
            - rack_width // 2
            + perspective_shift
        )

        right = (
            x
            + rack_width // 2
            + perspective_shift
        )

        draw.rounded_rectangle(
            (
                left,
                rack_top,
                right,
                rack_bottom,
            ),
            radius=max(
                8,
                rack_width // 8,
            ),
            fill=(43, 52, 48, 255),
            outline=(112, 118, 107, 180),
            width=max(
                2,
                width // 500,
            ),
        )

        slot_gap = max(
            10,
            int(
                (
                    rack_bottom
                    - rack_top
                )
                / 11
            ),
        )

        y = rack_top + slot_gap

        while (
            y
            < rack_bottom
            - slot_gap
        ):
            draw.line(
                (
                    left
                    + int(
                        rack_width
                        * 0.14
                    ),
                    y,
                    right
                    - int(
                        rack_width
                        * 0.14
                    ),
                    y,
                ),
                fill=(
                    131,
                    138,
                    126,
                    115,
                ),
                width=max(
                    1,
                    width // 900,
                ),
            )

            y += slot_gap

        for light_index in range(4):
            cy = (
                rack_top
                + int(
                    (
                        rack_bottom
                        - rack_top
                    )
                    * (
                        0.20
                        + light_index
                        * 0.17
                    )
                )
            )

            radius = max(
                2,
                width // 650,
            )

            draw.ellipse(
                (
                    right
                    - int(
                        rack_width
                        * 0.20
                    )
                    - radius,
                    cy - radius,
                    right
                    - int(
                        rack_width
                        * 0.20
                    )
                    + radius,
                    cy + radius,
                ),
                fill=(
                    183,
                    165,
                    123,
                    205,
                ),
            )

    random.seed(
        width * 1000
        + height
    )

    for _ in range(5):
        cx = random.randint(
            int(width * 0.1),
            int(width * 0.9),
        )

        cy = random.randint(
            int(height * 0.08),
            int(height * 0.45),
        )

        radius = random.randint(
            max(
                45,
                min(width, height)
                // 18,
            ),
            max(
                70,
                min(width, height)
                // 8,
            ),
        )

        glow = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 0),
        )

        glow_draw = ImageDraw.Draw(
            glow,
            "RGBA",
        )

        glow_draw.ellipse(
            (
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
            ),
            fill=(
                206,
                188,
                145,
                48,
            ),
        )

        glow = glow.filter(
            ImageFilter.GaussianBlur(
                radius=max(
                    18,
                    radius // 2,
                )
            )
        )

        image = Image.alpha_composite(
            image.convert(
                "RGBA"
            ),
            glow,
        ).convert(
            "RGB"
        )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
        optimize=True,
    )

    return buffer.getvalue()


def _generate_cloudflare_image(
    prompt: str,
    width: int,
    height: int,
) -> bytes:
    """
    Call Cloudflare Workers AI FLUX.1 Schnell.

    Cloudflare returns the generated image as Base64.
    The provider output is normalized locally into a PNG
    at the exact platform dimensions.
    """

    account_id = os.getenv(
        "CLOUDFLARE_ACCOUNT_ID"
    )

    api_token = os.getenv(
        "CLOUDFLARE_API_TOKEN"
    )

    if not account_id:
        raise RuntimeError(
            "CLOUDFLARE_ACCOUNT_ID is missing."
        )

    if not api_token:
        raise RuntimeError(
            "CLOUDFLARE_API_TOKEN is missing."
        )

    url = (
        "https://api.cloudflare.com/client/v4/"
        f"accounts/{account_id}/ai/run/"
        f"{CLOUDFLARE_MODEL}"
    )

    response = requests.post(
        url,
        headers={
            "Authorization": (
                f"Bearer {api_token}"
            ),
            "Content-Type": (
                "application/json"
            ),
        },
        json={
            "prompt": prompt,
            "steps": 4,
        },
        timeout=180,
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Cloudflare image generation failed: "
            f"{response.status_code} "
            f"{response.text[:700]}"
        )

    try:
        payload = response.json()

    except ValueError as error:
        raise RuntimeError(
            "Cloudflare returned invalid JSON."
        ) from error

    if not payload.get(
        "success",
        False,
    ):
        raise RuntimeError(
            "Cloudflare returned an unsuccessful "
            f"response: {str(payload)[:700]}"
        )

    result = payload.get(
        "result",
        {},
    )

    image_b64 = result.get(
        "image"
    )

    if not image_b64:
        raise RuntimeError(
            "Cloudflare returned no image."
        )

    try:
        provider_bytes = (
            base64.b64decode(
                image_b64
            )
        )

        return _normalize_provider_image(
            image_bytes=provider_bytes,
            width=width,
            height=height,
        )

    except Exception as error:
        raise RuntimeError(
            "Could not decode Cloudflare image."
        ) from error


@router.get("/generate")
def generate_image(
    prompt: str,
    platform: str = "hero",
    package_id: str | None = None,
):
    width, height = PLATFORM_SIZES.get(
        platform,
        PLATFORM_SIZES["hero"],
    )

    safe_platform = (
        platform
        if platform in PLATFORM_SIZES
        else "hero"
    )

    primary_prompt = (
        _build_primary_prompt(
            prompt=prompt,
            platform=safe_platform,
        )
    )

    provider_error = None
    fallback_used = False
    model_name = (
        "cloudflare-flux-1-schnell"
    )
    used_prompt = primary_prompt

    try:
        image_bytes = (
            _generate_cloudflare_image(
                prompt=primary_prompt,
                width=width,
                height=height,
            )
        )

    except Exception as error:
        provider_error = str(
            error
        )

        image_bytes = (
            _create_local_safe_fallback(
                width=width,
                height=height,
                platform=safe_platform,
            )
        )

        fallback_used = True
        model_name = (
            "local-safe-fallback"
        )
        used_prompt = (
            "Locally generated safe "
            "technology fallback."
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    safe_package_id = ""

    if package_id:
        safe_package_id = "".join(
            char
            for char in package_id
            if (
                char.isalnum()
                or char in ("-", "_")
            )
        )

    if safe_package_id:
        package_dir = (
            GENERATED_DIR
            / safe_package_id
        )

    else:
        package_dir = (
            GENERATED_DIR
        )

    package_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        f"{safe_platform}_"
        f"{timestamp}.png"
    )

    file_path = (
        package_dir
        / filename
    )

    try:
        file_path.write_bytes(
            image_bytes
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save generated "
                f"image: {error}"
            ),
        ) from error

    if package_id:
        update_package_asset(
            package_id=package_id,
            platform=safe_platform,
            asset={
                "filename": filename,
                "image_path": str(
                    file_path
                ),
                "width": width,
                "height": height,
                "model": model_name,
                "fallback_used":
                    fallback_used,
            },
        )

    encoded_image = (
        base64.b64encode(
            image_bytes
        ).decode(
            "ascii"
        )
    )

    image_url = (
        "data:image/png;base64,"
        f"{encoded_image}"
    )

    return {
        "status": "success",
        "package_id": package_id,
        "image_url": image_url,
        "image_path": str(
            file_path
        ),
        "filename": filename,
        "prompt": used_prompt,
        "platform": safe_platform,
        "width": width,
        "height": height,
        "model": model_name,
        "fallback_used":
            fallback_used,
        "provider_error":
            provider_error,
    }


@router.post("/upload-asset")
async def upload_asset(
    package_id: str = Form(...),
    platform: str = Form(...),
    file: UploadFile = File(...),
    slide: int | None = Form(None),
):
    """
    Save a frontend-rendered visual such as an infographic
    or carousel slide and link it to the package record.
    """

    allowed_platforms = {
        "infographic",
        "carousel",
        "quote",
    }

    if platform not in allowed_platforms:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported asset platform."
            ),
        )

    safe_package_id = "".join(
        char
        for char in package_id
        if char.isalnum()
        or char in ("-", "_")
    )

    if not safe_package_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid package_id.",
        )

    package_dir = (
        GENERATED_DIR
        / safe_package_id
    )

    package_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = (
        f"{platform}_"
        f"{timestamp}.png"
    )

    file_path = (
        package_dir
        / filename
    )

    try:
        image_bytes = (
            await file.read()
        )

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Uploaded image is empty."
                ),
            )

        file_path.write_bytes(
            image_bytes
        )

        linked = (
            update_package_asset(
                package_id=package_id,
                platform=platform,
                asset={
                    "slide": slide,
                    "filename": filename,
                    "image_path": str(
                        file_path
                    ),
                    "content_type": (
                        file.content_type
                        or "image/png"
                    ),
                },
            )
        )

        if not linked:
            try:
                file_path.unlink(
                    missing_ok=True
                )

            except OSError:
                pass

            raise HTTPException(
                status_code=404,
                detail=(
                    "Could not find the package "
                    "history record."
                ),
            )

        return {
            "status": "success",
            "package_id":
                package_id,
            "platform":
                platform,
            "filename":
                filename,
            "image_path": str(
                file_path
            ),
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save uploaded "
                f"asset: {error}"
            ),
        ) from error