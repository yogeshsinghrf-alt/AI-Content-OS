import json
from html import escape
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    KeepTogether,
    Image,
)


BACKEND_DIR = Path(__file__).resolve().parents[2]
EXPORTS_DIR = BACKEND_DIR / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# DESIGN TOKENS
# ---------------------------------------------------------

INK = colors.HexColor("#171615")
BODY = colors.HexColor("#403A35")
MUTED = colors.HexColor("#756D64")

CREAM = colors.HexColor("#F7F3EA")
SOFT_CREAM = colors.HexColor("#FBF9F5")
WARM_PANEL = colors.HexColor("#EEE5D8")
COOL_PANEL = colors.HexColor("#E5ECE8")

BORDER = colors.HexColor("#DDD3C5")
ACCENT = colors.HexColor("#A97850")
WHITE = colors.white


def _safe_text(value) -> str:
    if value is None:
        return ""

    if isinstance(value, dict):
        value = json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
        )

    if isinstance(value, list):
        return "<br/>".join(
            f"• {escape(str(item))}"
            for item in value
        )

    return escape(str(value)).replace(
        "\n",
        "<br/>",
    )


def _get_content(package: dict) -> dict:
    """
    Support both the new object format and older history
    files where content_package was stored as a JSON string.
    """

    content = package.get(
        "content_package",
        {},
    )

    if isinstance(content, dict):
        return content

    if isinstance(content, str):
        try:
            parsed = json.loads(content)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

        return {
            "generated_content": content
        }

    return {}

def _build_asset_image(
    asset: dict,
    max_width: float = 164 * mm,
    max_height: float = 190 * mm,
):
    """
    Create a ReportLab Image from a saved
    package asset while preserving aspect ratio.
    """

    if not isinstance(asset, dict):
        return None

    image_path = asset.get(
        "image_path"
    )

    if not image_path:
        return None

    path = Path(image_path)

    if not path.exists():
        return None

    try:
        image = Image(
            str(path)
        )

        original_width = float(
            image.imageWidth
        )

        original_height = float(
            image.imageHeight
        )

        if (
            original_width <= 0
            or original_height <= 0
        ):
            return None

        scale = min(
            max_width / original_width,
            max_height / original_height,
            1.0,
        )

        image.drawWidth = (
            original_width * scale
        )

        image.drawHeight = (
            original_height * scale
        )

        image.hAlign = "CENTER"

        return image

    except Exception as error:
        print(
            f"Could not load PDF asset "
            f"{image_path}: {error}"
        )

        return None
def create_package_pdf(package: dict) -> str:
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    topic = str(
        package.get(
            "topic",
            "content",
        )
    ).lower()

    filename = (
        f"AI_Content_OS_{topic}_{timestamp}.pdf"
    )

    file_path = EXPORTS_DIR / filename

    content = _get_content(package)

    assets = package.get(
        "assets",
        {},
    )

    if not isinstance(assets, dict):
        assets = {}

    styles = getSampleStyleSheet()

    # -----------------------------------------------------
    # TYPOGRAPHY
    # -----------------------------------------------------

    eyebrow_style = ParagraphStyle(
        "Eyebrow",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        tracking=2.2,
        textColor=ACCENT,
        spaceAfter=6,
    )

    cover_title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Times-Roman",
        fontSize=31,
        leading=34,
        alignment=TA_LEFT,
        textColor=INK,
        spaceAfter=10,
    )

    cover_subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        textColor=MUTED,
        spaceAfter=18,
    )

    editorial_title_style = ParagraphStyle(
        "EditorialTitle",
        parent=styles["Heading1"],
        fontName="Times-Roman",
        fontSize=25,
        leading=29,
        textColor=INK,
        spaceAfter=10,
    )

    editorial_subtitle_style = ParagraphStyle(
        "EditorialSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        textColor=MUTED,
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Times-Roman",
        fontSize=19,
        leading=23,
        textColor=INK,
        spaceBefore=8,
        spaceAfter=10,
    )

    option_label_style = ParagraphStyle(
        "OptionLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        tracking=1.5,
        textColor=ACCENT,
        spaceAfter=7,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=15,
        textColor=BODY,
        spaceAfter=8,
    )

    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=13,
        textColor=MUTED,
        spaceAfter=4,
    )

    quote_style = ParagraphStyle(
        "Quote",
        parent=styles["BodyText"],
        fontName="Times-Italic",
        fontSize=17,
        leading=23,
        textColor=INK,
        alignment=TA_LEFT,
    )

    takeaway_number_style = ParagraphStyle(
        "TakeawayNumber",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=22,
        leading=25,
        textColor=ACCENT,
    )

    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=MUTED,
        alignment=TA_CENTER,
    )

    # -----------------------------------------------------
    # DOCUMENT
    # -----------------------------------------------------

    document = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="AI Content OS Editorial Brief",
        author="AI Content OS",
    )

    story = []

    # -----------------------------------------------------
    # COVER / STORY INFORMATION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "AI CONTENT OS  /  DAILY INTELLIGENCE",
            eyebrow_style,
        )
    )

    story.append(
        Paragraph(
            "Editorial Content Brief",
            cover_title_style,
        )
    )

    story.append(
        Paragraph(
            (
                "Grounded AI-powered editorial and "
                "social content prepared from a "
                "selected industry story."
            ),
            cover_subtitle_style,
        )
    )

    metadata = [
        [
            Paragraph(
                "<b>TOPIC</b><br/>"
                + _safe_text(
                    package.get(
                        "topic",
                        "",
                    )
                ).upper(),
                meta_style,
            ),
            Paragraph(
                "<b>SOURCE</b><br/>"
                + _safe_text(
                    package.get(
                        "source",
                        "",
                    )
                ),
                meta_style,
            ),
        ],
        [
            Paragraph(
                "<b>DATE</b><br/>"
                + datetime.now().strftime(
                    "%d %B %Y"
                ),
                meta_style,
            ),
            Paragraph(
                "<b>CONTENT SYSTEM</b><br/>"
                "AI Content OS",
                meta_style,
            ),
        ],
    ]

    meta_table = Table(
        metadata,
        colWidths=[
            82 * mm,
            82 * mm,
        ],
    )

    meta_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    CREAM,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BORDER,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    story.append(meta_table)
    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "SOURCE STORY",
            eyebrow_style,
        )
    )

    story.append(
        Paragraph(
            _safe_text(
                package.get(
                    "article_title",
                    "",
                )
            ),
            heading_style,
        )
    )

    article_link = package.get(
        "article_link",
        "",
    )

    if article_link:
        story.append(
            Paragraph(
                _safe_text(article_link),
                meta_style,
            )
        )

    story.append(Spacer(1, 14))

    # -----------------------------------------------------
    # EDITORIAL POSITIONING
    # -----------------------------------------------------

    headline = content.get(
        "editorial_headline"
    )

    subtitle = content.get(
        "editorial_subtitle"
    )

    if headline:
        story.append(
            Paragraph(
                "EDITORIAL ANGLE",
                eyebrow_style,
            )
        )

        story.append(
            Paragraph(
                _safe_text(headline),
                editorial_title_style,
            )
        )

    if subtitle:
        story.append(
            Paragraph(
                _safe_text(subtitle),
                editorial_subtitle_style,
            )
        )

    # -----------------------------------------------------
    # KEY TAKEAWAYS
    # -----------------------------------------------------

    points = content.get(
        "infographic_points",
        [],
    )

    if points:
        story.append(
            Paragraph(
                "KEY TAKEAWAYS",
                eyebrow_style,
            )
        )

        takeaway_rows = []

        for index, point in enumerate(
            points,
            start=1,
        ):
            takeaway_rows.append(
                [
                    Paragraph(
                        f"{index:02}",
                        takeaway_number_style,
                    ),
                    Paragraph(
                        _safe_text(point),
                        body_style,
                    ),
                ]
            )

        takeaway_table = Table(
            takeaway_rows,
            colWidths=[
                17 * mm,
                147 * mm,
            ],
        )

        takeaway_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        SOFT_CREAM,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        BORDER,
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        BORDER,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                ]
            )
        )

        story.append(takeaway_table)

    story.append(PageBreak())

    # -----------------------------------------------------
    # LINKEDIN
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "SOCIAL COPY STUDIO",
            eyebrow_style,
        )
    )

    story.append(
        Paragraph(
            "LinkedIn",
            heading_style,
        )
    )

    for index, key in enumerate(
        [
            "linkedin_option_1",
            "linkedin_option_2",
        ],
        start=1,
    ):
        value = content.get(key)

        if not value:
            continue

        card = Table(
            [
                [
                    Paragraph(
                        f"OPTION {index:02}",
                        option_label_style,
                    )
                ],
                [
                    Paragraph(
                        _safe_text(value),
                        body_style,
                    )
                ],
            ],
            colWidths=[164 * mm],
        )

        card.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        SOFT_CREAM,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        BORDER,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        12,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        12,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                ]
            )
        )

        story.append(card)
        story.append(Spacer(1, 10))

    # -----------------------------------------------------
    # X + INSTAGRAM
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "X",
            heading_style,
        )
    )

    for index, key in enumerate(
        [
            "x_option_1",
            "x_option_2",
        ],
        start=1,
    ):
        value = content.get(key)

        if value:
            story.append(
                KeepTogether(
                    [
                        Paragraph(
                            f"OPTION {index:02}",
                            option_label_style,
                        ),
                        Paragraph(
                            _safe_text(value),
                            body_style,
                        ),
                        Spacer(1, 7),
                    ]
                )
            )

    story.append(
        Paragraph(
            "Instagram",
            heading_style,
        )
    )

    for index, key in enumerate(
        [
            "instagram_option_1",
            "instagram_option_2",
        ],
        start=1,
    ):
        value = content.get(key)

        if value:
            story.append(
                KeepTogether(
                    [
                        Paragraph(
                            f"OPTION {index:02}",
                            option_label_style,
                        ),
                        Paragraph(
                            _safe_text(value),
                            body_style,
                        ),
                        Spacer(1, 8),
                    ]
                )
            )

    story.append(PageBreak())
        # -----------------------------------------------------
    # GENERATED VISUAL ASSETS
    # -----------------------------------------------------

    available_visuals = []

    for asset_key, platform, label in [
        (
            "linkedin_creative_1",
            "linkedin 1",
            "LINKEDIN FINAL CREATIVE 1",
        ),
        (
            "linkedin_creative_2",
            "linkedin 2",
            "LINKEDIN FINAL CREATIVE 2",
        ),
        (
            "instagram_creative_1",
            "instagram 1",
            "INSTAGRAM FINAL CREATIVE 1",
        ),
        (
            "instagram_creative_2",
            "instagram 2",
            "INSTAGRAM FINAL CREATIVE 2",
        ),
        (
            "x_creative_1",
            "x 1",
            "X FINAL CREATIVE 1",
        ),
        (
            "x_creative_2",
            "x 2",
            "X FINAL CREATIVE 2",
        ),
    ]:
        asset = assets.get(
            asset_key
        )

        image = _build_asset_image(
            asset
        )

        if image:
            available_visuals.append(
                (
                    platform,
                    label,
                    asset,
                    image,
                )
            )

    if available_visuals:
        story.append(
            Paragraph(
                "GENERATED VISUAL ASSETS",
                eyebrow_style,
            )
        )

        story.append(
            Paragraph(
                "Platform-ready artwork",
                heading_style,
            )
        )

        story.append(
            Paragraph(
                (
                    "Generated visual assets associated "
                    "with this exact content package."
                ),
                cover_subtitle_style,
            )
        )

        for index, (
            platform,
            label,
            asset,
            image,
        ) in enumerate(
            available_visuals
        ):
            if index > 0:
                story.append(
                    PageBreak()
                )

            story.append(
                Paragraph(
                    label,
                    option_label_style,
                )
            )

            story.append(
                Spacer(
                    1,
                    6,
                )
            )

            story.append(
                image
            )

            story.append(
                Spacer(
                    1,
                    10,
                )
            )

            dimensions = (
                f"{asset.get('width', '')}"
                f" × "
                f"{asset.get('height', '')}"
            )

            story.append(
                Paragraph(
                    (
                        f"<b>Platform:</b> "
                        f"{_safe_text(platform).upper()}"
                        f"<br/>"
                        f"<b>Dimensions:</b> "
                        f"{_safe_text(dimensions)}"
                    ),
                    meta_style,
                )
            )

        story.append(
            PageBreak()
        )

    # -----------------------------------------------------
    # INFOGRAPHIC ASSET
    # -----------------------------------------------------

    infographic_asset = assets.get(
        "infographic"
    )

    infographic_image = _build_asset_image(
        infographic_asset,
        max_width=150 * mm,
        max_height=215 * mm,
    )

    if infographic_image:
        story.append(
            Paragraph(
                "INFOGRAPHIC",
                eyebrow_style,
            )
        )

        story.append(
            Paragraph(
                "Visual intelligence summary",
                heading_style,
            )
        )

        story.append(
            Paragraph(
                (
                    "The rendered infographic created "
                    "for this exact content package."
                ),
                cover_subtitle_style,
            )
        )

        story.append(
            infographic_image
        )

        story.append(
            PageBreak()
        )

    # -----------------------------------------------------
    # CAROUSEL ASSETS
    # -----------------------------------------------------

    carousel_assets = assets.get(
        "carousel",
        [],
    )

    if isinstance(
        carousel_assets,
        list,
    ):
        carousel_assets = sorted(
            carousel_assets,
            key=lambda item: (
                item.get("slide")
                if isinstance(item, dict)
                else 999
            ),
        )
    else:
        carousel_assets = []

    if carousel_assets:
        story.append(
            Paragraph(
                "EDITORIAL CAROUSEL",
                eyebrow_style,
            )
        )

        story.append(
            Paragraph(
                "6-slide swipe story",
                heading_style,
            )
        )

        story.append(
            Paragraph(
                (
                    "Rendered carousel slides associated "
                    "with this exact content package."
                ),
                cover_subtitle_style,
            )
        )

        for index, asset in enumerate(
            carousel_assets
        ):
            if not isinstance(
                asset,
                dict,
            ):
                continue

            carousel_image = _build_asset_image(
                asset,
                max_width=160 * mm,
                max_height=160 * mm,
            )

            if not carousel_image:
                continue

            if index > 0:
                story.append(
                    PageBreak()
                )

            slide_number = asset.get(
                "slide",
                index + 1,
            )

            story.append(
                Paragraph(
                    f"SLIDE {slide_number}",
                    option_label_style,
                )
            )

            story.append(
                Spacer(
                    1,
                    6,
                )
            )

            story.append(
                carousel_image
            )

            story.append(
                Spacer(
                    1,
                    10,
                )
            )

            story.append(
                Paragraph(
                    (
                        f"<b>Carousel slide:</b> "
                        f"{_safe_text(slide_number)} / "
                        f"{len(carousel_assets)}"
                    ),
                    meta_style,
                )
            )

        story.append(
            PageBreak()
        )

    # -----------------------------------------------------
    # QUOTE CARD
    # -----------------------------------------------------

    quote = content.get(
        "quote_card"
    )

    if quote:
        story.append(
            Paragraph(
                "QUOTE CARD",
                eyebrow_style,
            )
        )

        quote_table = Table(
            [
                [
                    Paragraph(
                        "“"
                        + _safe_text(quote)
                        + "”",
                        quote_style,
                    )
                ]
            ],
            colWidths=[164 * mm],
        )

        quote_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        WARM_PANEL,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        BORDER,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        18,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        18,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        18,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        18,
                    ),
                ]
            )
        )

        story.append(quote_table)
        story.append(Spacer(1, 20))

    # -----------------------------------------------------
    # VISUAL DIRECTION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "CREATIVE DIRECTION",
            eyebrow_style,
        )
    )

    story.append(
        Paragraph(
            "Visual concepts",
            heading_style,
        )
    )

    visual_sections = [
        (
            "HERO IMAGE",
            content.get(
                "hero_image_prompt"
            ),
        ),
        (
            "EDITORIAL IMAGE",
            content.get(
                "editorial_image_prompt"
            ),
        ),
        (
            "INSTAGRAM VISUAL",
            content.get(
                "instagram_visual_prompt"
            ),
        ),
        (
            "INFOGRAPHIC",
            content.get(
                "infographic_visual_prompt"
            ),
        ),
    ]

    for label, value in visual_sections:
        if not value:
            continue

        visual_card = Table(
            [
                [
                    Paragraph(
                        label,
                        option_label_style,
                    )
                ],
                [
                    Paragraph(
                        _safe_text(value),
                        body_style,
                    )
                ],
            ],
            colWidths=[164 * mm],
        )

        visual_card.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        COOL_PANEL,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        BORDER,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        12,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        12,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                ]
            )
        )

        story.append(visual_card)
        story.append(Spacer(1, 9))

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "AI CONTENT OS  •  GROUNDED EDITORIAL INTELLIGENCE",
            footer_style,
        )
    )

    document.build(story)

    return str(file_path)