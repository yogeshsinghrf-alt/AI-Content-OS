from fastapi import APIRouter, Query
import feedparser
import json
from datetime import datetime
from app.ai.gemini_service import generate_summary
from app.services.package_service import save_package

router = APIRouter()

RSS_FEEDS = {
    "ai": [
        ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
        ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
        ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
        ("MarkTechPost", "https://www.marktechpost.com/feed/"),
        ("Unite AI", "https://www.unite.ai/feed/")
    ],
    "telecom": [
        ("Telecoms.com", "https://www.telecoms.com/feed"),
        ("RCR Wireless", "https://www.rcrwireless.com/feed"),
        ("TelecomTalk", "https://telecomtalk.info/feed")
    ],
    "marketing": [
        ("HubSpot Marketing", "https://blog.hubspot.com/marketing/rss.xml"),
        ("Neil Patel Blog", "https://neilpatel.com/blog/feed/"),
        ("Buffer Blog", "https://buffer.com/resources/feed/")
    ]
}


@router.get("/daily")
@router.get("/daily")
def daily_package(topic: str = Query(default="ai")):
    feeds = RSS_FEEDS.get(
        topic,
        RSS_FEEDS["ai"],
    )

    all_articles = []

    for source_name, feed_url in feeds:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
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
                    "title": entry.title,
                    "link": entry.link,
                    "published_timestamp": published_timestamp,
                }
            )

    if not all_articles:
        return {
            "status": "error",
            "message": "No news articles found",
        }

    # -------------------------------------------------
    # 1. Remove duplicate article titles
    # -------------------------------------------------

    unique_articles = []
    seen_titles = set()

    for article in all_articles:
        normalized_title = (
            article["title"]
            .strip()
            .lower()
        )

        if normalized_title in seen_titles:
            continue

        seen_titles.add(normalized_title)
        unique_articles.append(article)

    # -------------------------------------------------
    # 2. Rotate preferred source every day
    # -------------------------------------------------

    today = datetime.now()

    day_number = today.toordinal()

    source_names = [
        source_name
        for source_name, _ in feeds
    ]

    preferred_source_index = (
        day_number % len(source_names)
    )

    preferred_source = source_names[
        preferred_source_index
    ]

    preferred_articles = [
        article
        for article in unique_articles
        if article["source"] == preferred_source
    ]

    # -------------------------------------------------
    # 3. Prefer the newest article from today's source
    # -------------------------------------------------

    candidates = (
        preferred_articles
        if preferred_articles
        else unique_articles
    )

    candidates.sort(
        key=lambda article: (
            article["published_timestamp"]
            or 0
        ),
        reverse=True,
    )

    # Select among the first few recent stories
    # so the exact article also changes.
    recent_candidates = candidates[:3]

    article_index = (
        day_number
        + sum(ord(char) for char in topic)
    ) % len(recent_candidates)

    article = recent_candidates[
        article_index
    ]

    news_text = f"""
Source: {article["source"]}
Title: {article["title"]}
Link: {article["link"]}
"""

    prompt = f"""
You are an AI content strategist.

News:
{news_text}

Return ONLY valid JSON.
No markdown.
No explanation.

The content must be specific to the selected news story.
Do not use generic AI language.
Do not invent statistics or facts not present in the story.

Create clearly different writing styles for each platform.

Use exactly this JSON structure:

{{
  "editorial_headline": "Short premium editorial headline in the style of a business magazine.",

  "editorial_subtitle": "One concise sentence supporting the headline.",

  "linkedin_option_1": "Professional LinkedIn post under 130 words. Insight-led, credible and business focused. End with 3 relevant hashtags.",

  "linkedin_option_2": "Thought-leadership LinkedIn post under 130 words using a different angle from option 1. End with 3 relevant hashtags.",

  "x_option_1": "Concise X post under 260 characters focused on the strongest news insight. Use maximum 2 hashtags.",

  "x_option_2": "Alternative X post under 260 characters with a different angle. Use maximum 2 hashtags.",

  "instagram_option_1": "Instagram caption under 80 words. More visual and conversational than LinkedIn. End with maximum 5 hashtags.",

  "instagram_option_2": "Alternative Instagram caption under 80 words using a different hook. End with maximum 5 hashtags.",

  "quote_card": "One short original insight inspired by the story. Do not falsely attribute it to a famous person.",

  "infographic_points": [
    "Key development",
    "Why it matters",
    "What to watch next",
    "Business or industry implication"
  ],

  "hero_image_prompt": "Premium visual direction directly related to this news story. Modern editorial aesthetic, sophisticated light palette, strong visual concept, no written text.",

  "editorial_image_prompt": "Business magazine visual direction directly related to the story. Premium European/US editorial style, elegant composition, no text.",

  "instagram_visual_prompt": "Portrait social visual directly related to the story. Expressive magazine composition, contemporary editorial photography or illustration, no text.",

  "infographic_visual_prompt": "Professional infographic direction directly related to the story using structured visual hierarchy, icons or data-inspired elements, light editorial palette."
}}
"""

    content_package = generate_summary(
        prompt
    )

    response = {
        "status": "success",
        "topic": topic,
        "source": article["source"],
        "article_title": article["title"],
        "article_link": article["link"],
        "available_sources": [
            source[0]
            for source in feeds
        ],
        "selection_info": {
            "preferred_source": preferred_source,
            "candidate_articles": len(
                unique_articles
            ),
            "selection_date": today.strftime(
                "%Y-%m-%d"
            ),
        },
        "content_package": content_package,
    }

    save_package(
        response,
        topic,
    )

    return response