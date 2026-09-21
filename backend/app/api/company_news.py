from datetime import datetime
import json
from urllib.parse import urlparse

from fastapi import (
    APIRouter,
    HTTPException,
)
from pydantic import BaseModel

from app.ai.gemini_service import (
    AIQuotaError,
    AIServiceError,
    generate_summary,
)
from app.services.article_service import (
    fetch_article_text,
    fetch_article_title,
)
from app.services.package_service import (
    save_package,
)


router = APIRouter()


class CompanyNewsRequest(BaseModel):
    article_url: str

    brand_enabled: bool = False
    brand_name: str = ""
    brand_audience: str = ""
    brand_tone: str = ""
    brand_cta: str = ""
    brand_primary_color: str = ""
    brand_secondary_color: str = ""


def clean_value(
    value: str,
    max_length: int = 250,
):
    return " ".join(
        str(value or "").split()
    )[:max_length]

def parse_json_response(
    raw_text: str,
):
    text = str(
        raw_text or ""
    ).strip()

    # Remove Markdown code fences when Gemini
    # wraps an otherwise valid JSON response.
    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip()
            == "```"
        ):
            lines = lines[:-1]

        text = "\n".join(
            lines
        ).strip()

    try:
        result = json.loads(
            text
        )

        if isinstance(
            result,
            dict,
        ):
            return result

    except json.JSONDecodeError:
        pass

    # Gemini can occasionally place a short
    # explanation around the JSON object.
    first_brace = text.find("{")

    if first_brace == -1:
        raise AIServiceError(
            "Gemini response did not contain JSON."
        )

    decoder = json.JSONDecoder()

    try:
        result, _ = decoder.raw_decode(
            text[first_brace:]
        )

        if not isinstance(
            result,
            dict,
        ):
            raise AIServiceError(
                "Gemini JSON response "
                "was not an object."
            )

        return result

    except json.JSONDecodeError as error:
        print(
            "COMPANY NEWS JSON PARSE ERROR:",
            str(error),
        )

        print(
            "GEMINI RESPONSE PREVIEW:",
            text[:800],
        )

        raise AIServiceError(
            "Gemini returned invalid JSON."
        ) from error
def get_source_name(
    article_url: str,
    brand_name: str,
):
    if brand_name.strip():
        return brand_name.strip()

    try:
        hostname = (
            urlparse(article_url)
            .hostname
            or ""
        )

        return (
            hostname
            .replace("www.", "")
            or "Company Newsroom"
        )

    except Exception:
        return "Company Newsroom"


@router.post("/company-news")
def generate_company_news(
    request: CompanyNewsRequest,
):
    article_url = clean_value(
        request.article_url,
        1000,
    )

    if not article_url.startswith(
        ("https://", "http://")
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_COMPANY_NEWS_URL",
                "message":
                    "Please provide a valid public article URL.",
            },
        )

    article_text = fetch_article_text(
        article_url,
        max_chars=16000,
    )

    if not article_text:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "COMPANY_NEWS_FETCH_FAILED",
                "message": (
                    "The company article could not be read. "
                    "Please check that the page is publicly accessible."
                ),
            },
        )
    article_title = (
        fetch_article_title(
            article_url
        )
        or "Company Announcement"
    )
    brand_profile = {
        "enabled":
            request.brand_enabled,
        "company_name":
            clean_value(
                request.brand_name,
                120,
            ),
        "audience":
            clean_value(
                request.brand_audience,
                200,
            ),
        "tone":
            clean_value(
                request.brand_tone,
                200,
            ),
        "cta":
            clean_value(
                request.brand_cta,
                160,
            ),
        "primary_color":
            clean_value(
                request.brand_primary_color,
                30,
            ),
        "secondary_color":
            clean_value(
                request.brand_secondary_color,
                30,
            ),
    }

    source_name = get_source_name(
        article_url,
        brand_profile[
            "company_name"
        ],
    )

    if request.brand_enabled:
        brand_context = f"""
BRAND PROFILE

Publishing organisation:
{brand_profile["company_name"]}

Target audience:
{brand_profile["audience"]}

Tone:
{brand_profile["tone"]}

Preferred CTA:
{brand_profile["cta"]}

Primary colour:
{brand_profile["primary_color"]}

Secondary colour:
{brand_profile["secondary_color"]}
"""
    else:
        brand_context = """
BRAND PROFILE

No organisation-specific Brand Profile is active.
Use a neutral professional corporate communications style.
"""

    prompt = f"""
You are a senior corporate communications editor.

You are transforming ONE organisation-owned announcement
into a complete communication package.

SOURCE URL:
{article_url}
SOURCE TITLE:
{article_title}
SOURCE ORGANISATION:
{source_name}

SOURCE CONTENT:
{article_text}

{brand_context}

CRITICAL GROUNDING RULES:

- Use ONLY the supplied source content.
- Do not invent statistics, dates, quotes,
  product claims, partnerships or outcomes.
- Do not imply facts that are not present
  in the source article.
- The organisation owns this announcement,
  so you may write in the organisation's
  publishing voice.
- Keep factual meaning consistent across outputs.

COMMUNICATION OBJECTIVE:

Create several distinct ways to communicate the SAME
announcement to different social audiences.

LINKEDIN OPTION 1:
Executive / strategic framing.

LINKEDIN OPTION 2:
Business-impact / audience-relevance framing.

INSTAGRAM OPTION 1:
Concise editorial / human-interest framing.

INSTAGRAM OPTION 2:
Brand / announcement framing.

X OPTION 1:
Straight news framing.

X OPTION 2:
Implication / takeaway framing.

INFOGRAPHIC:
One headline, one subtitle and exactly four points.

CAROUSEL:
One headline and exactly six slide objects.

VISUAL DIRECTIONS:

Each social option must have a distinct physical/editorial
image direction.

No logos.
No written text.
No dashboards.
No fake UI.
No posters.

If Brand Profile is active, visual prompts should prefer
the supplied colour palette where appropriate.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "linkedin_option_1": {{
    "headline": "Headline",
    "insight": "One-sentence implication",
    "post": "LinkedIn post",
    "visual_prompt": "Editorial image direction"
  }},
  "linkedin_option_2": {{
    "headline": "Headline",
    "insight": "One-sentence implication",
    "post": "LinkedIn post",
    "visual_prompt": "Editorial image direction"
  }},
  "instagram_option_1": {{
    "headline": "Headline",
    "insight": "One-sentence implication",
    "caption": "Instagram caption",
    "visual_prompt": "Portrait image direction"
  }},
  "instagram_option_2": {{
    "headline": "Headline",
    "insight": "One-sentence implication",
    "caption": "Instagram caption",
    "visual_prompt": "Portrait image direction"
  }},
  "x_option_1": {{
    "headline": "Headline",
    "insight": "One-sentence implication",
    "post": "X post",
    "visual_prompt": "Landscape image direction"
  }},
  "x_option_2": {{
    "headline": "Headline",
    "insight": "One-sentence implication",
    "post": "X post",
    "visual_prompt": "Landscape image direction"
  }},
  "infographic": {{
    "headline": "Infographic headline",
    "subtitle": "Supporting sentence",
    "points": [
      "Point one",
      "Point two",
      "Point three",
      "Point four"
    ]
  }},
  "carousel": {{
    "headline": "Carousel headline",
    "slides": [
      {{
        "label": "01",
        "title": "Slide title",
        "body": "Concise body"
      }},
      {{
        "label": "02",
        "title": "Slide title",
        "body": "Concise body"
      }},
      {{
        "label": "03",
        "title": "Slide title",
        "body": "Concise body"
      }},
      {{
        "label": "04",
        "title": "Slide title",
        "body": "Concise body"
      }},
      {{
        "label": "05",
        "title": "Slide title",
        "body": "Concise body"
      }},
      {{
        "label": "06",
        "title": "Slide title",
        "body": "Concise body"
      }}
    ]
  }}
}}
"""

    try:
        raw_package = generate_summary(
            prompt
        )

        generated = (
            parse_json_response(
                raw_package
            )
        )

        linkedin_1 = generated.get(
            "linkedin_option_1",
            {},
        )

        linkedin_2 = generated.get(
            "linkedin_option_2",
            {},
        )

        instagram_1 = generated.get(
            "instagram_option_1",
            {},
        )

        instagram_2 = generated.get(
            "instagram_option_2",
            {},
        )

        x_1 = generated.get(
            "x_option_1",
            {},
        )

        x_2 = generated.get(
            "x_option_2",
            {},
        )

        infographic = generated.get(
            "infographic",
            {},
        )

        carousel = generated.get(
            "carousel",
            {},
        )

        content_package = {
            "editorial_headline":
                str(
                    linkedin_1.get(
                        "headline",
                        "Company News",
                    )
                ),

            "editorial_subtitle":
                str(
                    infographic.get(
                        "subtitle",
                        "",
                    )
                ),

            "linkedin_option_1":
                str(
                    linkedin_1.get(
                        "post",
                        "",
                    )
                ),

            "linkedin_option_2":
                str(
                    linkedin_2.get(
                        "post",
                        "",
                    )
                ),

            "instagram_option_1":
                str(
                    instagram_1.get(
                        "caption",
                        "",
                    )
                ),

            "instagram_option_2":
                str(
                    instagram_2.get(
                        "caption",
                        "",
                    )
                ),

            "x_option_1":
                str(
                    x_1.get(
                        "post",
                        "",
                    )
                ),

            "x_option_2":
                str(
                    x_2.get(
                        "post",
                        "",
                    )
                ),

            "linkedin_1_headline":
                str(
                    linkedin_1.get(
                        "headline",
                        "",
                    )
                ),

            "linkedin_2_headline":
                str(
                    linkedin_2.get(
                        "headline",
                        "",
                    )
                ),

            "instagram_1_headline":
                str(
                    instagram_1.get(
                        "headline",
                        "",
                    )
                ),

            "instagram_2_headline":
                str(
                    instagram_2.get(
                        "headline",
                        "",
                    )
                ),

            "x_1_headline":
                str(
                    x_1.get(
                        "headline",
                        "",
                    )
                ),

            "x_2_headline":
                str(
                    x_2.get(
                        "headline",
                        "",
                    )
                ),

            "linkedin_1_visual_prompt":
                str(
                    linkedin_1.get(
                        "visual_prompt",
                        "",
                    )
                ),

            "linkedin_2_visual_prompt":
                str(
                    linkedin_2.get(
                        "visual_prompt",
                        "",
                    )
                ),

            "instagram_1_visual_prompt":
                str(
                    instagram_1.get(
                        "visual_prompt",
                        "",
                    )
                ),

            "instagram_2_visual_prompt":
                str(
                    instagram_2.get(
                        "visual_prompt",
                        "",
                    )
                ),

            "x_1_visual_prompt":
                str(
                    x_1.get(
                        "visual_prompt",
                        "",
                    )
                ),

            "x_2_visual_prompt":
                str(
                    x_2.get(
                        "visual_prompt",
                        "",
                    )
                ),

            "editorial_image_prompt":
                str(
                    linkedin_1.get(
                        "visual_prompt",
                        "",
                    )
                ),

            "instagram_visual_prompt":
                str(
                    instagram_1.get(
                        "visual_prompt",
                        "",
                    )
                ),

            "hero_image_prompt":
                str(
                    x_1.get(
                        "visual_prompt",
                        "",
                    )
                ),

            "infographic_headline":
                str(
                    infographic.get(
                        "headline",
                        "",
                    )
                ),

            "infographic_points":
                infographic.get(
                    "points",
                    [],
                ),

            "carousel_headline":
                str(
                    carousel.get(
                        "headline",
                        "",
                    )
                ),

            "carousel_slides":
                carousel.get(
                    "slides",
                    [],
                ),
        }

    except AIQuotaError:
        raise HTTPException(
            status_code=503,
            detail={
                "code":
                    "AI_QUOTA_UNAVAILABLE",
                "message":
                    "AI generation quota is temporarily unavailable.",
            },
        )

    except AIServiceError:
        raise HTTPException(
            status_code=503,
            detail={
                "code":
                    "AI_SERVICE_UNAVAILABLE",
                "message":
                    "The AI content service is temporarily unavailable.",
            },
        )

    package_id = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    slot_names = [
        "linkedin_1",
        "linkedin_2",
        "instagram_1",
        "instagram_2",
        "x_1",
        "x_2",
        "infographic",
        "carousel",
    ]

    stories = [
        {
            "slot": slot,
            "source": source_name,
            "title": article_title,
            "link": article_url,
        }
        for slot in slot_names
    ]

    response = {
        "status": "success",
        "package_id": package_id,
        "topic": "company-news",
        "source_mode": "company-news",
        "brand_profile":
            brand_profile,
        "source": source_name,
        "article_title":
            article_title,
        "article_link":
            article_url,
        "stories":
            stories,
        "available_sources": [
            source_name
        ],
        "selection_info": {
            "source_mode":
                "company-news",
            "single_source":
                True,
            "selection_date":
                datetime.now().strftime(
                    "%Y-%m-%d"
                ),
        },
        "content_package":
            content_package,
        "assets": {},
    }

    save_package(
        response,
        "company-news",
    )

    return response