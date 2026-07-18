from fastapi import APIRouter
import feedparser

router = APIRouter()

RSS_FEED = "https://huggingface.co/blog/feed.xml"


@router.get("/latest")
def latest_news():
    feed = feedparser.parse(RSS_FEED)

    articles = []

    for entry in feed.entries[:5]:
        articles.append(
            {
                "title": entry.title,
                "link": entry.link,
                "source": "Hugging Face Blog"
            }
        )

    return articles