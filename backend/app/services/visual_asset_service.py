import base64
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

from app.services.package_service import (
    update_package_asset,
)


load_dotenv()


BACKEND_DIR = Path(__file__).resolve().parents[2]
GENERATED_DIR = BACKEND_DIR / "generated_images"


def _load_font(
    size: int,
    bold: bool = False,
):
    """
    Use common Windows fonts if available.
    Fall back to Pillow default font.
    """

    candidates = []

    if bold:
        candidates.extend(
            [
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/calibrib.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
            ]
        )

    for font_path in candidates:
        path = Path(font_path)

        if path.exists():
            return ImageFont.truetype(
                str(path),
                size=size,
            )

    return ImageFont.load_default()

def _load_project_font(
    filename: str,
    size: int,
):
    """
    Load a font bundled with the project.
    """

    font_path = (
        BACKEND_DIR
        / "assets"
        / "fonts"
        / filename
    )

    if not font_path.exists():
        raise FileNotFoundError(
            f"Project font not found: {font_path}"
        )

    return ImageFont.truetype(
        str(font_path),
        size=size,
    )


def _draw_wrapped_text(
    draw,
    text: str,
    xy: tuple[int, int],
    font,
    fill,
    max_width: int,
    line_spacing: int = 10,
):
    """
    Draw wrapped text and return the final y position.
    """

    x, y = xy

    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = (
            f"{current} {word}".strip()
        )

        bbox = draw.textbbox(
            (0, 0),
            test,
            font=font,
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    for line in lines:
        draw.text(
            (x, y),
            line,
            font=font,
            fill=fill,
        )

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font,
        )

        line_height = (
            bbox[3] - bbox[1]
        )

        y += (
            line_height
            + line_spacing
        )

    return y



def _get_story_source(
    package: dict,
    slot: str,
    fallback: str = "AI Content OS",
):
    """
    Return the source assigned to a specific multi-story slot.
    Falls back to the package-level source for older packages.
    """

    stories = package.get(
        "stories",
        [],
    )

    if isinstance(stories, list):
        for story in stories:
            if not isinstance(story, dict):
                continue

            if story.get("slot") == slot:
                source = str(
                    story.get(
                        "source",
                        "",
                    )
                ).strip()

                if source:
                    return source

    source = str(
        package.get(
            "source",
            fallback,
        )
    ).strip()

    return source or fallback


def create_infographic_asset(
    package: dict,
):
    """
    Render a backend-generated 1080x1350 infographic
    and attach it to the exact package_id.
    """

    package_id = package.get(
        "package_id"
    )

    if not package_id:
        raise ValueError(
            "package_id is missing."
        )

    content = package.get(
        "content_package",
        {},
    )

    if not isinstance(
        content,
        dict,
    ):
        raise ValueError(
            "content_package must be a dictionary."
        )

    headline = str(
        content.get(
            "infographic_headline",
            content.get(
                "editorial_headline",
                package.get(
                 "article_title",
                 "Industry Intelligence",
                ),
           ),
      )
    ).strip()

    subtitle = str(
        content.get(
            "editorial_subtitle",
            "",
        )
    )

    points = content.get(
        "infographic_points",
        [],
    )

    if not isinstance(
        points,
        list,
    ):
        points = []

    while len(points) < 4:
        points.append(
            "Additional insight unavailable."
        )

    safe_package_id = "".join(
        char
        for char in package_id
        if char.isalnum()
        or char in ("-", "_")
    )

    package_dir = (
        GENERATED_DIR
        / safe_package_id
    )

    package_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = (
        package_dir
        / "infographic_scheduled.png"
    )

    image = Image.new(
        "RGB",
        (1080, 1350),
        "#F7F1E7",
    )

    draw = ImageDraw.Draw(
        image
    )

    eyebrow_font = _load_font(
        30,
        bold=True,
    )

    headline_font = _load_font(
        62,
        bold=True,
    )

    subtitle_font = _load_font(
        34,
        bold=False,
    )

    number_font = _load_font(
        48,
        bold=True,
    )

    label_font = _load_font(
        26,
        bold=True,
    )

    body_font = _load_font(
        32,
        bold=False,
    )

    footer_font = _load_font(
        24,
        bold=True,
    )

    ink = "#171615"
    muted = "#6B6259"
    accent = "#9A8167"

    draw.text(
        (70, 70),
        "AI CONTENT OS  /  DATA STORY",
        font=eyebrow_font,
        fill=accent,
    )

    current_y = 140

    current_y = _draw_wrapped_text(
        draw,
        headline,
        (70, current_y),
        headline_font,
        ink,
        max_width=940,
        line_spacing=8,
    )

    current_y += 20

    if subtitle:
        current_y = _draw_wrapped_text(
            draw,
            subtitle,
            (70, current_y),
            subtitle_font,
            muted,
            max_width=940,
            line_spacing=8,
        )

    current_y += 35

    labels = [
        "THE DEVELOPMENT",
        "WHY IT MATTERS",
        "WHAT TO WATCH",
        "BUSINESS IMPACT",
    ]

    box_width = 455
    box_height = 330

    positions = [
        (70, current_y),
        (555, current_y),
        (70, current_y + 360),
        (555, current_y + 360),
    ]

    fills = [
        "#E9DED0",
        "#E0E8E1",
        "#FFFDF8",
        "#EEE9DF",
    ]

    for index in range(4):
        x, y = positions[index]

        draw.rounded_rectangle(
            [
                x,
                y,
                x + box_width,
                y + box_height,
            ],
            radius=28,
            fill=fills[index],
            outline="#D4C9BA",
            width=2,
        )

        draw.text(
            (x + 28, y + 24),
            f"0{index + 1}",
            font=number_font,
            fill="#B2A18C",
        )

        draw.text(
            (x + 28, y + 90),
            labels[index],
            font=label_font,
            fill="#84776A",
        )

        point_text = str(
            points[index]
        )

        body_size = 32

        while body_size >= 22:
            test_font = _load_font(
                body_size,
                bold=False,
            )

            words = point_text.split()
            lines = []
            current = ""

            for word in words:
                test_line = (
                    f"{current} {word}".strip()
                )

                bbox = draw.textbbox(
                    (0, 0),
                    test_line,
                    font=test_font,
                )

                line_width = (
                    bbox[2] - bbox[0]
                )

                if line_width <= 395:
                    current = test_line
                else:
                    if current:
                        lines.append(
                            current
                        )

                    current = word

            if current:
                lines.append(
                    current
                )

            line_heights = []

            for line in lines:
                bbox = draw.textbbox(
                    (0, 0),
                    line,
                    font=test_font,
                )

                line_heights.append(
                    bbox[3] - bbox[1]
                )

            total_height = sum(
                line_heights
            )

            total_height += (
                max(
                    0,
                    len(lines) - 1,
                )
                * 7
            )

            if total_height <= 155:
                break

            body_size -= 2

        fitted_body_font = _load_font(
            body_size,
            bold=False,
        )

        _draw_wrapped_text(
            draw,
            point_text,
            (x + 28, y + 145),
            fitted_body_font,
            "#302D29",
            max_width=395,
            line_spacing=7,
        )

    draw.text(
        (70, 1285),
        _get_story_source(
            package,
            "infographic",
        )[:60],
        font=footer_font,
        fill="#81766A",
    )

    image.save(
        file_path,
        format="PNG",
    )

    update_package_asset(
        package_id=package_id,
        platform="infographic",
        asset={
            "filename": file_path.name,
            "image_path": str(file_path),
            "width": 1080,
            "height": 1350,
            "renderer": "pillow-backend",
        },
    )

    return {
        "status": "success",
        "platform": "infographic",
        "filename": file_path.name,
        "image_path": str(file_path),
    }

def create_carousel_assets(
    package: dict,
):
    """
    Render six square carousel slides on the backend
    and attach them to the exact package_id.
    """

    package_id = package.get(
        "package_id"
    )

    if not package_id:
        raise ValueError(
            "package_id is missing."
        )

    content = package.get(
        "content_package",
        {},
    )

    if not isinstance(
        content,
        dict,
    ):
        raise ValueError(
            "content_package must be a dictionary."
        )

    headline = str(
        content.get(
            "carousel_headline",
            content.get(
                "editorial_headline",
            package.get(
                "article_title",
                "Industry Intelligence",
            ),
          )
       )
    )
    subtitle = str(
        content.get(
            "editorial_subtitle",
            "",
        )
    )

    points = content.get(
        "infographic_points",
        [],
    )

    if not isinstance(
        points,
        list,
    ):
        points = []

    while len(points) < 4:
        points.append(
            "Additional insight unavailable."
        )

    source = _get_story_source(
        package,
        "carousel",
    )

    safe_package_id = "".join(
        char
        for char in package_id
        if char.isalnum()
        or char in ("-", "_")
    )

    package_dir = (
        GENERATED_DIR
        / safe_package_id
    )

    package_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    carousel_slides = content.get(
        "carousel_slides",
        [],
    )

    slides = []

    if (
        isinstance(
            carousel_slides,
            list,
        )
        and len(carousel_slides) == 6
    ):
        for index, slide in enumerate(
            carousel_slides,
            start=1,
        ):
            if not isinstance(
                slide,
                dict,
            ):
                continue

            slides.append(
                {
                    "label": str(
                        slide.get(
                            "label",
                            f"{index:02}",
                        )
                    ),
                    "title": str(
                        slide.get(
                            "title",
                            "",
                        )
                    ),
                    "body": str(
                        slide.get(
                            "body",
                            "",
                        )
                    ),
                }
            )

    # Backward-compatible fallback for
    # older single-story packages.
    if len(slides) != 6:
        slides = [
            {
                "label": "THE BIG IDEA",
                "title": headline,
                "body": subtitle,
            },
            {
                "label": "01 / THE DEVELOPMENT",
                "title": "What changed?",
                "body": str(points[0]),
            },
            {
                "label": "02 / WHY IT MATTERS",
                "title": "Why this matters",
                "body": str(points[1]),
            },
            {
                "label": "03 / WHAT TO WATCH",
                "title": "What happens next?",
                "body": str(points[2]),
            },
            {
                "label": "04 / BUSINESS IMPACT",
                "title": "The business implication",
                "body": str(points[3]),
            },
            {
                "label": "THE TAKEAWAY",
                "title": headline,
                "body": (
                    "Follow the development as adoption, "
                    "commercial impact and industry response evolve."
                ),
            },
        ]
    backgrounds = [
        "#F7F1E7",
        "#E9DED0",
        "#E0E8E1",
        "#FFFDF8",
        "#EEE9DF",
        "#F3EBDD",
    ]

    eyebrow_font = _load_font(
        28,
        bold=True,
    )

    title_font = _load_font(
        70,
        bold=True,
    )

    body_font = _load_font(
        38,
        bold=False,
    )

    footer_font = _load_font(
        24,
        bold=True,
    )

    saved_assets = []

    for index, slide_data in enumerate(
        slides,
        start=1,
    ):
        image = Image.new(
            "RGB",
            (1080, 1080),
            backgrounds[index - 1],
        )

        draw = ImageDraw.Draw(
            image
        )

        draw.text(
            (75, 75),
            slide_data["label"],
            font=eyebrow_font,
            fill="#927F68",
        )

        current_y = 190

        current_y = _draw_wrapped_text(
            draw,
            slide_data["title"],
            (75, current_y),
            title_font,
            "#171615",
            max_width=920,
            line_spacing=10,
        )

        current_y += 40

        _draw_wrapped_text(
            draw,
            slide_data["body"],
            (75, current_y),
            body_font,
            "#514A43",
            max_width=900,
            line_spacing=12,
        )

        draw.line(
            (
                75,
                945,
                1005,
                945,
            ),
            fill="#D0C5B6",
            width=2,
        )

        draw.text(
            (75, 975),
            source[:50],
            font=footer_font,
            fill="#81766A",
        )

        slide_marker = (
            f"{index:02} / 06"
        )

        marker_bbox = draw.textbbox(
            (0, 0),
            slide_marker,
            font=footer_font,
        )

        marker_width = (
            marker_bbox[2]
            - marker_bbox[0]
        )

        draw.text(
            (
                1005 - marker_width,
                975,
            ),
            slide_marker,
            font=footer_font,
            fill="#81766A",
        )

        file_path = (
            package_dir
            / f"carousel_scheduled_{index:02}.png"
        )

        image.save(
            file_path,
            format="PNG",
        )

        asset = {
            "slide": index,
            "filename": file_path.name,
            "image_path": str(file_path),
            "width": 1080,
            "height": 1080,
            "renderer": "pillow-backend",
        }

        update_package_asset(
            package_id=package_id,
            platform="carousel",
            asset=asset,
        )

        saved_assets.append(
            asset
        )

    return {
        "status": "success",
        "platform": "carousel",
        "slides": len(saved_assets),
        "assets": saved_assets,
    }

def create_social_image_asset(
    package: dict,
    platform: str,
    option: int = 1,
):
    """
    Generate a social image through Pollinations.

    If the first generation appears to be a safety-filter
    placeholder, retry once with a neutral editorial prompt.
    """

    platform_sizes = {
        "linkedin": (1200, 1200),
        "instagram": (1080, 1350),
        "x": (1600, 900),
    }

    if platform not in platform_sizes:
        raise ValueError(
            f"Unsupported social platform: {platform}"
        )

    if option not in (1, 2):
        raise ValueError(
            f"Unsupported social option: {option}"
        )

    package_id = package.get(
        "package_id"
    )

    if not package_id:
        raise ValueError(
            "package_id is missing."
        )

    content = package.get(
        "content_package",
        {},
    )

    if not isinstance(content, dict):
        raise ValueError(
            "content_package must be a dictionary."
        )

    api_key = os.getenv(
        "POLLINATIONS_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "POLLINATIONS_API_KEY is missing."
        )

    width, height = platform_sizes[
        platform
    ]

    prompt_keys = {
        ("linkedin", 1): "linkedin_1_visual_prompt",
        ("linkedin", 2): "linkedin_2_visual_prompt",
        ("instagram", 1): "instagram_1_visual_prompt",
        ("instagram", 2): "instagram_2_visual_prompt",
        ("x", 1): "x_1_visual_prompt",
        ("x", 2): "x_2_visual_prompt",
    }

    prompt = str(
        content.get(
            prompt_keys[
                (platform, option)
            ],
            "",
        )
    ).strip()

    if not prompt:
        legacy_prompt_keys = {
            "linkedin": "editorial_image_prompt",
            "instagram": "instagram_visual_prompt",
            "x": "hero_image_prompt",
        }

        prompt = str(
            content.get(
                legacy_prompt_keys[
                    platform
                ],
                "",
            )
        ).strip()

    if not prompt:
        prompt = (
            "Modern enterprise technology "
            "infrastructure in a professional setting."
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

    clean_prompt = prompt

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

    instructions = {
        "linkedin": (
            "Square executive business editorial "
            "photograph with sophisticated professional "
            "composition and generous negative space."
        ),
        "instagram": (
            "Portrait editorial photograph with strong "
            "visual storytelling, premium magazine styling "
            "and elegant composition."
        ),
        "x": (
            "Wide editorial photograph with one strong "
            "visual focal point and generous negative space."
        ),
    }

    final_prompt = f"""
{instructions[platform]}

Create a neutral editorial photograph inspired by this subject:

{clean_prompt}

Represent the subject through ordinary real-world environments,
architecture, infrastructure, equipment or abstract physical
technology details.

Do not depict dangerous activity, weapons, injury, explicit
content, political persuasion or identifiable private people.

High-end international business editorial photography.
Photorealistic.
Natural cinematic lighting.
Warm neutral palette.
Realistic materials.
Architectural depth.
Clean professional composition.

No text.
No letters.
No numbers.
No signs.
No captions.
No logos.
No brands.
No watermark.
No user interface.
No dashboard.
No computer screen content.
""".strip()

    fallback_prompt = f"""
{instructions[platform]}

Create a neutral premium business editorial photograph.

Show a modern professional technology environment using
architecture, server infrastructure, fiber infrastructure,
laboratory equipment or abstract physical technology details.

No people are required.
No brands.
No company identities.
No controversial subject matter.
No dangerous activity.
No weapons.
No injury.
No politics.

Photorealistic international business publication photography.
Natural cinematic lighting.
Warm neutral colors.
Realistic physical materials.
Clean sophisticated composition.
Generous negative space.

No text.
No letters.
No numbers.
No signs.
No captions.
No logos.
No watermark.
No interface.
No dashboard.
No screen content.
""".strip()

    headers = {
        "Authorization": (
            f"Bearer {api_key}"
        ),
        "Content-Type": "application/json",
    }

    def request_image(
        image_prompt: str,
    ) -> bytes:
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
            raise RuntimeError(
                "Pollinations image generation failed "
                f"for {platform}: "
                f"{response.status_code} "
                f"{response.text[:500]}"
            )

        try:
            result = response.json()

        except ValueError as error:
            raise RuntimeError(
                "Pollinations returned invalid JSON."
            ) from error

        data = result.get(
            "data",
            [],
        )

        if not data:
            raise RuntimeError(
                f"Pollinations returned no image "
                f"for {platform}."
            )

        b64_image = data[0].get(
            "b64_json"
        )

        if not b64_image:
            raise RuntimeError(
                f"Pollinations returned no base64 "
                f"image for {platform}."
            )

        try:
            return base64.b64decode(
                b64_image
            )

        except Exception as error:
            raise RuntimeError(
                f"Could not decode {platform} image."
            ) from error

    def image_looks_blocked(
        image_bytes: bytes,
    ) -> bool:
        """
        Detect the common Pollinations safety-placeholder
        layout without OCR.

        This is intentionally conservative. It detects
        unusually flat placeholder-style images rather
        than attempting to read rendered text.
        """

        try:
            from io import BytesIO

            test_image = Image.open(
                BytesIO(image_bytes)
            ).convert("RGB")

            test_image.thumbnail(
                (160, 160)
            )

            colors = test_image.getcolors(
                maxcolors=160 * 160
            )

            if colors is None:
                return False

            unique_colors = len(colors)

            # Normal photographs usually contain many
            # thousands of colors. Filter/error cards are
            # commonly much flatter.
            return unique_colors < 120

        except Exception:
            return False

    image_bytes = request_image(
        final_prompt
    )

    if image_looks_blocked(
        image_bytes
    ):
        print(
            f"Possible safety placeholder detected for "
            f"{platform} option {option}. Retrying "
            f"with neutral fallback prompt."
        )

        image_bytes = request_image(
            fallback_prompt
        )

        if image_looks_blocked(
            image_bytes
        ):
            raise RuntimeError(
                "Pollinations returned a probable "
                "safety-filter placeholder after retry "
                f"for {platform} option {option}."
            )

    safe_package_id = "".join(
        char
        for char in str(package_id)
        if char.isalnum()
        or char in ("-", "_")
    )

    package_dir = (
        GENERATED_DIR
        / safe_package_id
    )

    package_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = (
        package_dir
        / (
            f"{platform}_scheduled_"
            f"{option}.png"
        )
    )

    with file_path.open(
        "wb"
    ) as file:
        file.write(
            image_bytes
        )

    asset = {
        "option": option,
        "filename": file_path.name,
        "image_path": str(file_path),
        "width": width,
        "height": height,
        "model": "pollinations-zimage",
        "renderer": "pollinations-backend",
    }

    update_package_asset(
        package_id=package_id,
        platform=(
            f"{platform}_{option}"
        ),
        asset=asset,
    )

    return {
        "status": "success",
        "platform": f"{platform}_{option}",
        "filename": file_path.name,
        "image_path": str(file_path),
        "width": width,
        "height": height,
    }

def create_linkedin_creative(
    package: dict,
    option: int = 1,
):
    """
    Build a finished 1200x1200 LinkedIn editorial creative
    using the matching scheduled raw image.
    """

    if option not in (1, 2):
        raise ValueError(
            f"Unsupported LinkedIn option: {option}"
        )

    package_id = package.get(
        "package_id"
    )

    if not package_id:
        raise ValueError(
            "package_id is missing."
        )

    content = package.get(
        "content_package",
        {},
    )

    if not isinstance(content, dict):
        raise ValueError(
            "content_package must be a dictionary."
        )

    headline = str(
        content.get(
            f"linkedin_{option}_headline",
            content.get(
                "editorial_headline",
                package.get(
                    "article_title",
                    "Industry Intelligence",
                ),
            ),
        )
    ).strip()

    insight = str(
        content.get(
            f"linkedin_{option}_insight",
            content.get(
                "editorial_subtitle",
                "",
            ),
        )
    ).strip()

    source = _get_story_source(
        package,
        f"linkedin_{option}",
    )

    safe_package_id = "".join(
        char
        for char in str(package_id)
        if char.isalnum()
        or char in ("-", "_")
    )

    package_dir = GENERATED_DIR / safe_package_id

    raw_image_path = (
        package_dir
        / f"linkedin_scheduled_{option}.png"
    )

    if not raw_image_path.exists():
        raise FileNotFoundError(
            f"{raw_image_path.name} was not found "
            f"for package {package_id}."
        )

    output_path = (
        package_dir
        / f"linkedin_creative_{option}.png"
    )

    canvas = Image.new(
        "RGB",
        (1200, 1200),
        "#F5F0E8",
    )

    draw = ImageDraw.Draw(canvas)

    eyebrow_font = _load_project_font(
        "Inter-SemiBold.ttf",
        21,
    )

    headline_font = _load_project_font(
        "InstrumentSerif-Regular.ttf",
        62,
    )

    insight_font = _load_project_font(
        "Inter-Regular.ttf",
        30,
    )

    footer_font = _load_project_font(
        "Inter-SemiBold.ttf",
        22,
    )

    ink = "#171615"
    muted = "#625B53"
    accent = "#9A8167"
    rule = "#CEC4B7"

    draw.text(
        (70, 55),
        "AI CONTENT OS",
        font=eyebrow_font,
        fill=accent,
    )

    section_label = "EDITORIAL INTELLIGENCE"
    label_bbox = draw.textbbox(
        (0, 0),
        section_label,
        font=eyebrow_font,
    )
    label_width = label_bbox[2] - label_bbox[0]

    draw.text(
        (1130 - label_width, 55),
        section_label,
        font=eyebrow_font,
        fill=muted,
    )

    raw_image = Image.open(
        raw_image_path
    ).convert("RGB")

    image_box = (
        70,
        115,
        1130,
        640,
    )

    box_width = image_box[2] - image_box[0]
    box_height = image_box[3] - image_box[1]

    image_ratio = raw_image.width / raw_image.height
    box_ratio = box_width / box_height

    if image_ratio > box_ratio:
        new_height = box_height
        new_width = int(new_height * image_ratio)
    else:
        new_width = box_width
        new_height = int(new_width / image_ratio)

    raw_image = raw_image.resize(
        (new_width, new_height),
        Image.LANCZOS,
    )

    left = max(
        0,
        (new_width - box_width) // 2,
    )
    top = max(
        0,
        (new_height - box_height) // 2,
    )

    raw_image = raw_image.crop(
        (
            left,
            top,
            left + box_width,
            top + box_height,
        )
    )

    canvas.paste(
        raw_image,
        (
            image_box[0],
            image_box[1],
        ),
    )

    current_y = 705

    current_y = _draw_wrapped_text(
        draw,
        headline,
        (70, current_y),
        headline_font,
        ink,
        max_width=1030,
        line_spacing=8,
    )

    if insight:
        current_y += 24

        _draw_wrapped_text(
            draw,
            insight,
            (70, current_y),
            insight_font,
            muted,
            max_width=900,
            line_spacing=8,
        )

    footer_y = 1100

    draw.line(
        (
            70,
            footer_y,
            1130,
            footer_y,
        ),
        fill=rule,
        width=2,
    )

    draw.text(
        (70, footer_y + 28),
        source[:60].upper(),
        font=footer_font,
        fill=muted,
    )

    brand = "AI CONTENT OS"
    brand_bbox = draw.textbbox(
        (0, 0),
        brand,
        font=footer_font,
    )
    brand_width = brand_bbox[2] - brand_bbox[0]

    draw.text(
        (
            1130 - brand_width,
            footer_y + 28,
        ),
        brand,
        font=footer_font,
        fill=accent,
    )

    canvas.save(
        output_path,
        format="PNG",
    )

    asset = {
        "option": option,
        "filename": output_path.name,
        "image_path": str(output_path),
        "width": 1200,
        "height": 1200,
        "renderer": "pillow-backend",
        "source_asset": raw_image_path.name,
        "source": source,
    }

    update_package_asset(
        package_id=package_id,
        platform=f"linkedin_creative_{option}",
        asset=asset,
    )

    return {
        "status": "success",
        "platform": f"linkedin_creative_{option}",
        "option": option,
        "filename": output_path.name,
        "image_path": str(output_path),
        "width": 1200,
        "height": 1200,
    }


def create_instagram_creative(
    package: dict,
    option: int = 1,
):
    """
    Build a finished 1080x1350 Instagram editorial creative
    using the matching scheduled raw image.
    """

    if option not in (1, 2):
        raise ValueError(
            f"Unsupported Instagram option: {option}"
        )

    package_id = package.get(
        "package_id"
    )

    if not package_id:
        raise ValueError(
            "package_id is missing."
        )

    content = package.get(
        "content_package",
        {},
    )

    if not isinstance(content, dict):
        raise ValueError(
            "content_package must be a dictionary."
        )

    headline = str(
        content.get(
            f"instagram_{option}_headline",
            content.get(
                "editorial_headline",
                package.get(
                    "article_title",
                    "Industry Intelligence",
                ),
            ),
        )
    ).strip()

    insight = str(
        content.get(
            f"instagram_{option}_insight",
            content.get(
                "editorial_subtitle",
                "",
            ),
        )
    ).strip()

    source = _get_story_source(
        package,
        f"instagram_{option}",
    )

    safe_package_id = "".join(
        char
        for char in str(package_id)
        if char.isalnum()
        or char in ("-", "_")
    )

    package_dir = GENERATED_DIR / safe_package_id

    raw_image_path = (
        package_dir
        / f"instagram_scheduled_{option}.png"
    )

    if not raw_image_path.exists():
        raise FileNotFoundError(
            f"{raw_image_path.name} was not found "
            f"for package {package_id}."
        )

    output_path = (
        package_dir
        / f"instagram_creative_{option}.png"
    )

    canvas = Image.new(
        "RGB",
        (1080, 1350),
        "#F5F0E8",
    )

    draw = ImageDraw.Draw(canvas)

    eyebrow_font = _load_project_font(
        "Inter-SemiBold.ttf",
        20,
    )

    headline_font = _load_project_font(
        "InstrumentSerif-Regular.ttf",
        60,
    )

    insight_font = _load_project_font(
        "Inter-Regular.ttf",
        28,
    )

    footer_font = _load_project_font(
        "Inter-SemiBold.ttf",
        21,
    )

    ink = "#171615"
    muted = "#625B53"
    accent = "#9A8167"
    rule = "#CEC4B7"

    draw.text(
        (60, 50),
        "AI CONTENT OS",
        font=eyebrow_font,
        fill=accent,
    )

    section_label = "EDITORIAL INTELLIGENCE"
    label_bbox = draw.textbbox(
        (0, 0),
        section_label,
        font=eyebrow_font,
    )
    label_width = label_bbox[2] - label_bbox[0]

    draw.text(
        (1020 - label_width, 50),
        section_label,
        font=eyebrow_font,
        fill=muted,
    )

    raw_image = Image.open(
        raw_image_path
    ).convert("RGB")

    image_box = (
        60,
        105,
        1020,
        760,
    )

    box_width = image_box[2] - image_box[0]
    box_height = image_box[3] - image_box[1]

    image_ratio = raw_image.width / raw_image.height
    box_ratio = box_width / box_height

    if image_ratio > box_ratio:
        new_height = box_height
        new_width = int(new_height * image_ratio)
    else:
        new_width = box_width
        new_height = int(new_width / image_ratio)

    raw_image = raw_image.resize(
        (new_width, new_height),
        Image.LANCZOS,
    )

    left = max(
        0,
        (new_width - box_width) // 2,
    )
    top = max(
        0,
        (new_height - box_height) // 2,
    )

    raw_image = raw_image.crop(
        (
            left,
            top,
            left + box_width,
            top + box_height,
        )
    )

    canvas.paste(
        raw_image,
        (
            image_box[0],
            image_box[1],
        ),
    )

    current_y = 815

    current_y = _draw_wrapped_text(
        draw,
        headline,
        (60, current_y),
        headline_font,
        ink,
        max_width=940,
        line_spacing=7,
    )

    if insight:
        current_y += 22

        _draw_wrapped_text(
            draw,
            insight,
            (60, current_y),
            insight_font,
            muted,
            max_width=860,
            line_spacing=8,
        )

    footer_y = 1250

    draw.line(
        (
            60,
            footer_y,
            1020,
            footer_y,
        ),
        fill=rule,
        width=2,
    )

    draw.text(
        (60, footer_y + 26),
        source[:60].upper(),
        font=footer_font,
        fill=muted,
    )

    brand = "AI CONTENT OS"
    brand_bbox = draw.textbbox(
        (0, 0),
        brand,
        font=footer_font,
    )
    brand_width = brand_bbox[2] - brand_bbox[0]

    draw.text(
        (
            1020 - brand_width,
            footer_y + 26,
        ),
        brand,
        font=footer_font,
        fill=accent,
    )

    canvas.save(
        output_path,
        format="PNG",
    )

    asset = {
        "option": option,
        "filename": output_path.name,
        "image_path": str(output_path),
        "width": 1080,
        "height": 1350,
        "renderer": "pillow-backend",
        "source_asset": raw_image_path.name,
        "source": source,
    }

    update_package_asset(
        package_id=package_id,
        platform=f"instagram_creative_{option}",
        asset=asset,
    )

    return {
        "status": "success",
        "platform": f"instagram_creative_{option}",
        "option": option,
        "filename": output_path.name,
        "image_path": str(output_path),
        "width": 1080,
        "height": 1350,
    }


def create_x_creative(
    package: dict,
    option: int = 1,
):
    """
    Build a finished 1600x900 X editorial creative
    using the matching scheduled raw image.
    """

    if option not in (1, 2):
        raise ValueError(
            f"Unsupported X option: {option}"
        )

    package_id = package.get(
        "package_id"
    )

    if not package_id:
        raise ValueError(
            "package_id is missing."
        )

    content = package.get(
        "content_package",
        {},
    )

    if not isinstance(content, dict):
        raise ValueError(
            "content_package must be a dictionary."
        )

    headline = str(
        content.get(
            f"x_{option}_headline",
            content.get(
                "editorial_headline",
                package.get(
                    "article_title",
                    "Industry Intelligence",
                ),
            ),
        )
    ).strip()

    insight = str(
        content.get(
            f"x_{option}_insight",
            content.get(
                "editorial_subtitle",
                "",
            ),
        )
    ).strip()

    source = _get_story_source(
        package,
        f"x_{option}",
    )

    safe_package_id = "".join(
        char
        for char in str(package_id)
        if char.isalnum()
        or char in ("-", "_")
    )

    package_dir = GENERATED_DIR / safe_package_id

    raw_image_path = (
        package_dir
        / f"x_scheduled_{option}.png"
    )

    if not raw_image_path.exists():
        raise FileNotFoundError(
            f"{raw_image_path.name} was not found "
            f"for package {package_id}."
        )

    output_path = (
        package_dir
        / f"x_creative_{option}.png"
    )

    canvas = Image.new(
        "RGB",
        (1600, 900),
        "#F5F0E8",
    )

    draw = ImageDraw.Draw(canvas)

    eyebrow_font = _load_project_font(
        "Inter-SemiBold.ttf",
        19,
    )

    headline_font = _load_project_font(
        "InstrumentSerif-Regular.ttf",
        58,
    )

    insight_font = _load_project_font(
        "Inter-Regular.ttf",
        25,
    )

    footer_font = _load_project_font(
        "Inter-SemiBold.ttf",
        19,
    )

    ink = "#171615"
    muted = "#625B53"
    accent = "#9A8167"
    rule = "#CEC4B7"

    draw.text(
        (65, 55),
        "AI CONTENT OS",
        font=eyebrow_font,
        fill=accent,
    )

    draw.text(
        (65, 105),
        "EDITORIAL INTELLIGENCE",
        font=eyebrow_font,
        fill=muted,
    )

    current_y = 190

    current_y = _draw_wrapped_text(
        draw,
        headline,
        (65, current_y),
        headline_font,
        ink,
        max_width=600,
        line_spacing=7,
    )

    if insight:
        current_y += 28

        _draw_wrapped_text(
            draw,
            insight,
            (65, current_y),
            insight_font,
            muted,
            max_width=560,
            line_spacing=8,
        )

    raw_image = Image.open(
        raw_image_path
    ).convert("RGB")

    image_box = (
        735,
        55,
        1535,
        785,
    )

    box_width = image_box[2] - image_box[0]
    box_height = image_box[3] - image_box[1]

    image_ratio = raw_image.width / raw_image.height
    box_ratio = box_width / box_height

    if image_ratio > box_ratio:
        new_height = box_height
        new_width = int(new_height * image_ratio)
    else:
        new_width = box_width
        new_height = int(new_width / image_ratio)

    raw_image = raw_image.resize(
        (new_width, new_height),
        Image.LANCZOS,
    )

    left = max(
        0,
        (new_width - box_width) // 2,
    )
    top = max(
        0,
        (new_height - box_height) // 2,
    )

    raw_image = raw_image.crop(
        (
            left,
            top,
            left + box_width,
            top + box_height,
        )
    )

    canvas.paste(
        raw_image,
        (
            image_box[0],
            image_box[1],
        ),
    )

    footer_y = 825

    draw.line(
        (
            65,
            footer_y,
            1535,
            footer_y,
        ),
        fill=rule,
        width=2,
    )

    draw.text(
        (65, footer_y + 25),
        source[:60].upper(),
        font=footer_font,
        fill=muted,
    )

    brand = "AI CONTENT OS"
    brand_bbox = draw.textbbox(
        (0, 0),
        brand,
        font=footer_font,
    )
    brand_width = brand_bbox[2] - brand_bbox[0]

    draw.text(
        (
            1535 - brand_width,
            footer_y + 25,
        ),
        brand,
        font=footer_font,
        fill=accent,
    )

    canvas.save(
        output_path,
        format="PNG",
    )

    asset = {
        "option": option,
        "filename": output_path.name,
        "image_path": str(output_path),
        "width": 1600,
        "height": 900,
        "renderer": "pillow-backend",
        "source_asset": raw_image_path.name,
        "source": source,
    }

    update_package_asset(
        package_id=package_id,
        platform=f"x_creative_{option}",
        asset=asset,
    )

    return {
        "status": "success",
        "platform": f"x_creative_{option}",
        "option": option,
        "filename": output_path.name,
        "image_path": str(output_path),
        "width": 1600,
        "height": 900,
    }

