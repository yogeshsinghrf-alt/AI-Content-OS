from fastapi import APIRouter, Query
import feedparser
import random
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
def daily_package(topic: str = Query(default="ai")):
    feeds = RSS_FEEDS.get(topic, RSS_FEEDS["ai"])

    all_articles = []

    for source_name, feed_url in feeds:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:3]:
            all_articles.append({
                "source": source_name,
                "title": entry.title,
                "link": entry.link
            })

    if not all_articles:
        return {
            "status": "error",
            "message": "No news articles found"
        }

    article = random.choice(all_articles)

    news_text = f"""
    Source: {article["source"]}
    Title: {article["title"]}
    Link: {article["link"]}
    """

    prompt = f"""
You are an AI content strategist.

News:
{news_text}

Return ONLY valid JSON. No markdown. No explanation.

Use exactly this JSON structure:

{{
  "editorial_headline": "Short premium editorial headline in the style of a business magazine.",
  "editorial_subtitle": "One sentence supporting the headline.",
  "linkedin_option_1": "Professional LinkedIn post under 130 words with 3 hashtags.",
  "linkedin_option_2": "Thought leadership LinkedIn post under 130 words with 3 hashtags.",
  "x_option_1": "X post under 260 characters with 2 hashtags.",
  "x_option_2": "X post under 260 characters with 2 hashtags.",
  "instagram_option_1": "Instagram caption under 80 words with 5 hashtags.",
  "instagram_option_2": "Instagram caption under 80 words with 5 hashtags.",
  "quote_card": "A short famous-style quote related to innovation, AI, business, or progress. No photo.",
  "infographic_points": ["Point 1", "Point 2", "Point 3"],
  "hero_image_prompt": "Premium visual prompt for a modern editorial AI/social media image, warm cream background, elegant typography, light colors, no people photos.",
  "editorial_image_prompt": "Editorial magazine cover image direction with warm cream colors, minimal design, premium European style.",
  "instagram_visual_prompt": "Instagram post visual direction using soft beige colors, elegant typography and modern layout.",
  "infographic_visual_prompt": "Modern infographic design with icons, clean layout, warm neutral colors and editorial styling."
}}
"""

    content_package = generate_summary(prompt)

    response = {
        "status": "success",
        "topic": topic,
        "source": article["source"],
        "article_title": article["title"],
        "article_link": article["link"],
        "available_sources": [source[0] for source in feeds],
        "content_package": content_package
    }

    save_package(response, topic)

    return response