from datetime import datetime
import json
import feedparser
from fastapi import APIRouter, HTTPException, Query

from app.ai.gemini_service import (
    AIQuotaError,
    AIServiceError,
    generate_summary,
)
from app.services.history_service import (
    get_last_used_source,
    get_recent_article_links,
    get_recent_article_titles,
)
from app.services.package_service import save_package
from app.services.article_service import fetch_article_text
from app.services.source_discovery_service import (
    discover_topic_articles,
)


router = APIRouter()


RSS_FEEDS = {
    "ai": [
        (
            "Hugging Face Blog",
            "https://huggingface.co/blog/feed.xml",
        ),
        (
            "VentureBeat AI",
            "https://venturebeat.com/category/ai/feed/",
        ),
        (
            "Google AI Blog",
            "https://blog.google/technology/ai/rss/",
        ),
        (
            "MarkTechPost",
            "https://www.marktechpost.com/feed/",
        ),
        (
            "OpenAI",
            "https://openai.com/news/rss.xml",
        ),
    ],

    "telecom": [
        (
            "Telecoms.com",
            "https://www.telecoms.com/feed",
        ),
        (
            "RCR Wireless",
            "https://www.rcrwireless.com/feed",
        ),
        (
            "TelecomTalk",
            "https://telecomtalk.info/feed",
        ),
    ],

    "marketing": [
        (
            "HubSpot Marketing",
            "https://blog.hubspot.com/marketing/rss.xml",
        ),
        (
            "Neil Patel Blog",
            "https://neilpatel.com/blog/feed/",
        ),
        (
            "Buffer Blog",
            "https://buffer.com/resources/feed/",
        ),
    ],
}


@router.get("/daily")
def daily_package(
    topic: str = Query(default="ai"),
):
    feeds = RSS_FEEDS.get(
        topic,
        RSS_FEEDS["ai"],
    )

    all_articles = []

    # -------------------------------------------------
    # 1. Read articles from all configured RSS feeds
    # -------------------------------------------------

    for source_name, feed_url in feeds:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            title = getattr(
                entry,
                "title",
                "",
            ).strip()

            link = getattr(
                entry,
                "link",
                "",
            ).strip()

            if not title or not link:
                continue

            published = getattr(
                entry,
                "published_parsed",
                None,
            )

            published_timestamp = None

            if published:
                try:
                    published_timestamp = datetime(
                        *published[:6]
                    ).timestamp()
                except Exception:
                    published_timestamp = None

            all_articles.append(
                {
                    "source": source_name,
                    "title": title,
                    "link": link,
                    "published_timestamp": published_timestamp,
                }
            )
    # -------------------------------------------------
    # Add HTML-discovered sources
    # -------------------------------------------------

    discovered_articles = (
        discover_topic_articles(
            topic=topic,
            limit_per_source=5,
        )
    )

    all_articles.extend(
        discovered_articles
    )
    if not all_articles:
        return {
            "status": "error",
            "message": "No news articles found.",
        }

    # -------------------------------------------------
    # 2. Remove duplicate titles within today's feeds
    # -------------------------------------------------

    unique_articles = []
    seen_titles = set()
    seen_links = set()

    for article in all_articles:
        normalized_title = (
            article["title"]
            .strip()
            .lower()
        )

        normalized_link = (
            article["link"]
            .strip()
        )

        if normalized_title in seen_titles:
            continue

        if normalized_link in seen_links:
            continue

        seen_titles.add(normalized_title)
        seen_links.add(normalized_link)

        unique_articles.append(article)

    # -------------------------------------------------
    # 3. Load recently used article history
    # -------------------------------------------------

    recent_titles = get_recent_article_titles(
        topic=topic,
        limit=30,
    )

    recent_links = get_recent_article_links(
        topic=topic,
        limit=30,
    )

    last_used_source = get_last_used_source(
        topic=topic,
    )

    # -------------------------------------------------
    # 4. Remove articles already used recently
    # -------------------------------------------------

    fresh_articles = []

    for article in unique_articles:
        normalized_title = (
            article["title"]
            .strip()
            .lower()
        )

        normalized_link = (
            article["link"]
            .strip()
        )

        if normalized_title in recent_titles:
            continue

        if normalized_link in recent_links:
            continue

        fresh_articles.append(article)

    # If all current feed articles have been used,
    # allow reuse rather than failing completely.
    used_history_fallback = False

    if not fresh_articles:
        fresh_articles = unique_articles
        used_history_fallback = True

        # -------------------------------------------------
    # 5. Build a diverse multi-story selection
    # -------------------------------------------------

    fresh_articles.sort(
        key=lambda article: (
            article["published_timestamp"]
            or 0
        ),
        reverse=True,
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

    selected_articles = []
    used_sources = set()
    used_links = set()

    # First pass:
    # prefer a new source for every slot.
    for article in fresh_articles:
        if len(selected_articles) >= len(
            slot_names
        ):
            break

        if article["link"] in used_links:
            continue

        if article["source"] in used_sources:
            continue

        selected_articles.append(
            article
        )

        used_links.add(
            article["link"]
        )

        used_sources.add(
            article["source"]
        )

    # Second pass:
    # if there are not enough publishers,
    # allow another fresh article from an
    # already-used source.
    if len(selected_articles) < len(
        slot_names
    ):
        for article in fresh_articles:
            if len(selected_articles) >= len(
                slot_names
            ):
                break

            if article["link"] in used_links:
                continue

            selected_articles.append(
                article
            )

            used_links.add(
                article["link"]
            )

            used_sources.add(
                article["source"]
            )

    if not selected_articles:
        return {
            "status": "error",
            "message": (
                "No usable fresh stories were found."
            ),
        }

    # If fewer than 8 fresh articles exist,
    # reuse the available article pool only
    # as a last-resort fallback.
    article_index = 0

    while len(selected_articles) < len(
        slot_names
    ):
        selected_articles.append(
            selected_articles[
                article_index
                % len(selected_articles)
            ]
        )

        article_index += 1

    selected_stories = []

    for slot, article in zip(
        slot_names,
        selected_articles,
    ):
        selected_stories.append(
            {
                "slot": slot,
                "source": article["source"],
                "title": article["title"],
                "link": article["link"],
            }
        )

    # -------------------------------------------------
    # 8. Fetch and prepare each assigned story
    # -------------------------------------------------

    grounded_stories = []

    for story in selected_stories:
        article_text = fetch_article_text(
            story["link"]
        )

        grounded_stories.append(
            {
                **story,
                "article_text": (
                    article_text
                    if article_text
                    else (
                        "[Full article text unavailable. "
                        "Use only the title and source "
                        "information for this story.]"
                    )
                ),
            }
        )

    stories_text = ""

    for story in grounded_stories:
        stories_text += f"""
SLOT: {story["slot"]}
SOURCE: {story["source"]}
TITLE: {story["title"]}
LINK: {story["link"]}

ARTICLE CONTENT:
{story["article_text"]}

----------------------------------------
"""

    # -------------------------------------------------
    # 9. Build one multi-story Gemini prompt
    # -------------------------------------------------

    prompt = f"""
You are an experienced technology and business editor.

You are creating a DAILY MULTI-STORY CONTENT PACKAGE.

Each content slot below has already been assigned a specific
news story.

CRITICAL RULE:

Each output MUST use ONLY the story assigned to its slot.

Do not combine facts between stories.
Do not move facts from one slot into another.
Do not invent facts, statistics, quotations, dates,
capabilities, outcomes or product claims.

If full article text is unavailable, remain conservative
and use only the supplied source and title.

ASSIGNED STORIES:

{stories_text}

CONTENT ASSIGNMENTS:

linkedin_option_1 must use SLOT linkedin_1 only.
linkedin_option_2 must use SLOT linkedin_2 only.

instagram_option_1 must use SLOT instagram_1 only.
instagram_option_2 must use SLOT instagram_2 only.

x_option_1 must use SLOT x_1 only.
x_option_2 must use SLOT x_2 only.

infographic must use SLOT infographic only.

carousel must use SLOT carousel only.

The stories should remain editorially independent.
Before returning the JSON, verify each output independently.

Every headline, insight, post, caption, infographic point,
carousel slide and visual prompt must contain information
from its assigned story only.

If the assigned story does not contain enough information
for a requested detail, omit that detail rather than using
information from another assigned story.
WRITING STANDARD:

- Write like a professional technology/business publication.
- Lead with implications rather than generic announcements.
- Use restrained, credible language.
- Avoid hype and generic AI phrases.
- Preserve uncertainty when a story concerns research.
- Never imply that two unrelated stories are connected.

LINKEDIN:
90-130 words each.
Executive/business intelligence style.
End with 3 relevant hashtags.

INSTAGRAM:
Maximum 70 words each.
Editorial, visual and conversational.
Maximum 5 hashtags.

X:
Maximum 240 characters each.
Sharp news intelligence.
Maximum 2 hashtags.

INFOGRAPHIC:
Create one headline, one subtitle and exactly four concise
points based ONLY on the infographic story.

CAROUSEL:
Create one headline and exactly six slide objects based ONLY
on the carousel story.

Each carousel slide requires:
- label
- title
- body

Keep slide body text concise enough for a 1080x1080 design.

VISUAL DIRECTIONS:

Generate a separate physical/editorial image direction for
LinkedIn 1, Instagram 1 and X 1.

No dashboards.
No fake interfaces.
No written text.
No logos.
No posters.
No UI mockups.

Return ONLY valid JSON.
No markdown.
No explanation.

Use exactly this JSON structure:

{{
  "linkedin_option_1": {{
    "headline": "Concise editorial headline.",
    "insight": "One short sentence explaining why this specific story matters.",
    "post": "LinkedIn post.",
    "visual_prompt": "Premium editorial image direction."
  }},

  "linkedin_option_2": {{
    "headline": "Concise editorial headline.",
    "insight": "One short sentence explaining why this specific story matters.",
    "post": "LinkedIn post.",
    "visual_prompt": "Premium editorial image direction."
  }},

  "instagram_option_1": {{
    "headline": "Concise editorial headline.",
    "insight": "One short sentence supporting this specific Instagram story.",
    "caption": "Instagram caption.",
    "visual_prompt": "Portrait editorial image direction."
  }},

   "instagram_option_2": {{
    "headline": "Concise editorial headline.",
    "insight": "One short sentence supporting this specific Instagram story.",
    "caption": "Instagram caption.",
    "visual_prompt": "Portrait editorial image direction."
}},

  "x_option_1": {{
    "headline": "Concise editorial headline.",
    "insight": "One short sentence explaining the significance of this specific X story.",
    "post": "X post.",
    "visual_prompt": "Landscape editorial image direction."
  }},

  "x_option_2": {{
    "headline": "Concise editorial headline.",
    "insight": "One short sentence explaining the significance of this specific X story.",
    "post": "X post.",
    "visual_prompt": "Landscape editorial image direction."
  }},

  "infographic": {{
    "headline": "Infographic headline.",
    "subtitle": "One precise supporting sentence.",
    "points": [
      "Point one",
      "Point two",
      "Point three",
      "Point four"
    ]
  }},

  "carousel": {{
    "headline": "Carousel headline.",
    "slides": [
      {{
        "label": "01",
        "title": "Slide title",
        "body": "Concise slide body."
      }},
      {{
        "label": "02",
        "title": "Slide title",
        "body": "Concise slide body."
      }},
      {{
        "label": "03",
        "title": "Slide title",
        "body": "Concise slide body."
      }},
      {{
        "label": "04",
        "title": "Slide title",
        "body": "Concise slide body."
      }},
      {{
        "label": "05",
        "title": "Slide title",
        "body": "Concise slide body."
      }},
      {{
        "label": "06",
        "title": "Slide title",
        "body": "Concise slide body."
      }}
    ]
  }}
}}
"""
    try:
        content_package = generate_summary(
            prompt
        )
        try:
            content_package = json.loads(
                content_package
            )
        except json.JSONDecodeError as error:
            raise AIServiceError(
                f"Gemini returned invalid JSON: {str(error)}"
            ) from error    
        # -------------------------------------------------
        # 10. Flatten multi-story Gemini output so existing
        # renderers/services continue to work unchanged.
        # -------------------------------------------------

        linkedin_1 = content_package.get(
            "linkedin_option_1",
            {},
        )

        linkedin_2 = content_package.get(
            "linkedin_option_2",
            {},
        )

        instagram_1 = content_package.get(
            "instagram_option_1",
            {},
        )

        instagram_2 = content_package.get(
            "instagram_option_2",
            {},
        )

        x_1 = content_package.get(
            "x_option_1",
            {},
        )

        x_2 = content_package.get(
            "x_option_2",
            {},
        )

        infographic = content_package.get(
            "infographic",
            {},
        )

        carousel = content_package.get(
            "carousel",
            {},
        )

        content_package = {
            # Shared editorial fields used by current renderers.
            "editorial_headline": str(
                linkedin_1.get(
                    "headline",
                    "Industry Intelligence",
                )
            ),
            "editorial_subtitle": str(
                infographic.get(
                    "subtitle",
                    "",
                )
            ),

            # Social copy.
            "linkedin_option_1": str(
                linkedin_1.get(
                    "post",
                    "",
                )
            ),
            "linkedin_option_2": str(
                linkedin_2.get(
                    "post",
                    "",
                )
            ),

            "instagram_option_1": str(
                instagram_1.get(
                    "caption",
                    "",
                )
            ),
            "instagram_option_2": str(
                instagram_2.get(
                    "caption",
                    "",
                )
            ),

            "x_option_1": str(
                x_1.get(
                    "post",
                    "",
                )
            ),
            "x_option_2": str(
                x_2.get(
                    "post",
                    "",
                )
            ),

            # Current visual generators.
            "editorial_image_prompt": str(
                linkedin_1.get(
                    "visual_prompt",
                    "",
                )
            ),
            "instagram_visual_prompt": str(
                instagram_1.get(
                    "visual_prompt",
                    "",
                )
            ),
            "hero_image_prompt": str(
                x_1.get(
                    "visual_prompt",
                    "",
                )
            ),

            # Infographic.
            "infographic_headline": str(
                infographic.get(
                    "headline",
                    "",
                )
            ),
            "infographic_points": (
                infographic.get(
                    "points",
                    [],
                )
            ),

            # Carousel-specific content.
            "carousel_headline": str(
                carousel.get(
                    "headline",
                    "",
                )
            ),
            "carousel_slides": (
                carousel.get(
                    "slides",
                    [],
                )
            ),

            # Keep slot-specific headlines available
            # for later renderer improvements.
            "linkedin_1_headline": str(
                linkedin_1.get(
                    "headline",
                    "",
                )
            ),
            "linkedin_1_insight": str(
                linkedin_1.get(
                    "insight",
                  "",
    )
            ),
            "linkedin_2_headline": str(
                linkedin_2.get(
                    "headline",
                    "",
                )
            ),
            "linkedin_2_insight": str(
    linkedin_2.get(
        "insight",
        "",
    )
),

"linkedin_2_visual_prompt": str(
    linkedin_2.get(
        "visual_prompt",
        "",
    )
),
            "instagram_1_headline": str(
                instagram_1.get(
                    "headline",
                    "",
                )
            ),
            "instagram_1_insight": str(
                instagram_1.get(
                    "insight",
                    "",
                )
            ),
            "instagram_2_headline": str(
                instagram_2.get(
                    "headline",
                    "",
                )
            ),
            "instagram_2_insight": str(
    instagram_2.get(
        "insight",
        "",
    )
),

"instagram_2_visual_prompt": str(
    instagram_2.get(
        "visual_prompt",
        "",
    )
),
            "x_1_headline": str(
                x_1.get(
                    "headline",
                    "",
                )
            ),
            "x_1_insight": str(
                x_1.get(
                    "insight",
                    "",
                )
            ),
            "x_2_headline": str(
                x_2.get(
                    "headline",
                    "",
                )
            ),
        "x_2_insight": str(
    x_2.get(
        "insight",
        "",
    )
),

"x_2_visual_prompt": str(
    x_2.get(
        "visual_prompt",
        "",
    )
),
"linkedin_1_visual_prompt": str(
    linkedin_1.get(
        "visual_prompt",
        "",
    )
),

"instagram_1_visual_prompt": str(
    instagram_1.get(
        "visual_prompt",
        "",
    )
),

"x_1_visual_prompt": str(
    x_1.get(
        "visual_prompt",
        "",
    )
),        
}

        
    except AIQuotaError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "AI_QUOTA_UNAVAILABLE",
                "message": (
                    "AI content generation is temporarily "
                    "unavailable because the provider quota "
                    "has been reached. Please try again later."
                ),
                "retryable": True,
            },
        )

    except AIServiceError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "AI_SERVICE_UNAVAILABLE",
                "message": (
                    "The AI content service is temporarily "
                    "unavailable. Please try again later."
                ),
                "retryable": True,
            },
        )

    # -------------------------------------------------
    # 9. Build response
    # -------------------------------------------------
    package_id = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )
    response = {
        "status": "success",
        "package_id": package_id,
        "topic": topic,
        "source": selected_stories[0]["source"],
        "article_title": selected_stories[0]["title"],
        "article_link": selected_stories[0]["link"],
        "stories": selected_stories,

        "available_sources": sorted(
    {
        article["source"]
        for article in all_articles
        if article.get("source")
    }
),

        "selection_info": {
            "last_used_source": last_used_source,

            "recent_titles_checked": len(
                recent_titles
            ),

            "recent_links_checked": len(
                recent_links
            ),

            "total_feed_articles": len(
                all_articles
            ),

            "unique_articles": len(
                unique_articles
            ),

            "fresh_candidates": len(
                fresh_articles
            ),

            "history_fallback_used":
                used_history_fallback,

            "selection_date":
                datetime.now().strftime(
                    "%Y-%m-%d"
                ),
        },

        "content_package":
            content_package,
        "assets": {},
    }

    # -------------------------------------------------
    # 10. Save package to history
    # -------------------------------------------------

    save_package(
        response,
        topic,
    )

    return response