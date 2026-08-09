from datetime import datetime

import feedparser
from fastapi import APIRouter, Query

from app.ai.gemini_service import generate_summary
from app.services.history_service import (
    get_last_used_source,
    get_recent_article_links,
    get_recent_article_titles,
)
from app.services.package_service import save_package


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
            "Unite AI",
            "https://www.unite.ai/feed/",
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
    # 5. Avoid using the same source consecutively
    # -------------------------------------------------

    alternative_source_articles = [
        article
        for article in fresh_articles
        if article["source"] != last_used_source
    ]

    if alternative_source_articles:
        fresh_articles = alternative_source_articles

    # -------------------------------------------------
    # 6. Sort newest articles first
    # -------------------------------------------------

    fresh_articles.sort(
        key=lambda article: (
            article["published_timestamp"]
            or 0
        ),
        reverse=True,
    )

    # -------------------------------------------------
    # 7. Rotate among the freshest five stories
    # -------------------------------------------------

    recent_candidates = fresh_articles[:5]

    day_number = datetime.now().toordinal()

    article_index = (
        day_number
        + sum(ord(char) for char in topic)
    ) % len(recent_candidates)

    article = recent_candidates[
        article_index
    ]

    # -------------------------------------------------
    # 8. Build Gemini content-generation prompt
    # -------------------------------------------------

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

Do not invent statistics, quotations,
product capabilities, dates, numbers,
or facts that are not supported by the
selected story.

Create clearly different writing styles
for each social platform.

Use exactly this JSON structure:

{{
  "editorial_headline":
    "Short premium editorial headline in the style of a business magazine.",

  "editorial_subtitle":
    "One concise sentence supporting the headline.",

  "linkedin_option_1":
    "Professional LinkedIn post under 130 words. Insight-led, credible and business focused. End with 3 relevant hashtags.",

  "linkedin_option_2":
    "Thought-leadership LinkedIn post under 130 words using a different angle from option 1. End with 3 relevant hashtags.",

  "x_option_1":
    "Concise X post under 260 characters focused on the strongest news insight. Use maximum 2 hashtags.",

  "x_option_2":
    "Alternative X post under 260 characters with a different angle. Use maximum 2 hashtags.",

  "instagram_option_1":
    "Instagram caption under 80 words. More visual and conversational than LinkedIn. End with maximum 5 hashtags.",

  "instagram_option_2":
    "Alternative Instagram caption under 80 words using a different hook. End with maximum 5 hashtags.",

  "quote_card":
    "One short original insight inspired by the story. Do not falsely attribute it to a famous person.",

  "infographic_points": [
    "Key development",
    "Why it matters",
    "What to watch next",
    "Business or industry implication"
  ],

  "hero_image_prompt":
    "Premium visual direction directly related to this news story. Modern editorial aesthetic, sophisticated light palette, strong visual concept, no written text.",

  "editorial_image_prompt":
    "Business magazine visual direction directly related to the story. Premium European/US editorial style, elegant composition, no text.",

  "instagram_visual_prompt":
    "Portrait social visual directly related to the story. Expressive magazine composition, contemporary editorial photography or illustration, no text.",

  "infographic_visual_prompt":
    "Professional infographic direction directly related to the story using structured visual hierarchy, icons or data-inspired elements, light editorial palette.",

  "visual_mode_1":
    "Editorial carousel-cover concept based specifically on the selected story.",

  "visual_mode_2":
    "Minimal quote-card concept based specifically on the selected story.",

  "visual_mode_3":
    "Professional infographic concept summarizing the selected story.",

  "visual_mode_4":
    "Premium Instagram visual concept based specifically on the selected story."
}}
"""

    content_package = generate_summary(
        prompt
    )

    # -------------------------------------------------
    # 9. Build response
    # -------------------------------------------------

    response = {
        "status": "success",
        "topic": topic,
        "source": article["source"],
        "article_title": article["title"],
        "article_link": article["link"],

        "available_sources": [
            source_name
            for source_name, _ in feeds
        ],

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
    }

    # -------------------------------------------------
    # 10. Save package to history
    # -------------------------------------------------

    save_package(
        response,
        topic,
    )

    return response