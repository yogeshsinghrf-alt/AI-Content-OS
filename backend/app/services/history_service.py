import os
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
HISTORY_DIR = BASE_DIR / "history"


def list_history():
    files = []

    if not os.path.exists(HISTORY_DIR):
        return files

    for file in sorted(
        os.listdir(HISTORY_DIR),
        reverse=True,
    ):
        if not file.endswith(".json"):
            continue

        file_path = os.path.join(
            HISTORY_DIR,
            file,
        )

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as f:
                data = json.load(f)

            files.append(
                {
                    "filename": file,
                    "topic": data.get("topic"),
                    "title": data.get(
                        "article_title"
                    ),
                    "link": data.get(
                        "article_link"
                    ),
                    "source": data.get("source"),
                }
            )

        except (
            json.JSONDecodeError,
            OSError,
        ) as error:
            print(
                f"Could not read history "
                f"{file}: {error}"
            )

    return files


def get_history_file(
    filename: str,
):
    file_path = os.path.join(
        HISTORY_DIR,
        filename,
    )

    if not os.path.exists(file_path):
        return None

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return None


def delete_history_file(
    filename: str,
):
    file_path = os.path.join(
        HISTORY_DIR,
        filename,
    )

    if os.path.exists(file_path):
        os.remove(file_path)
        return True

    return False


def get_latest_history_file():
    files = list_history()

    if not files:
        return None

    latest = files[0]

    return get_history_file(
        latest["filename"]
    )


def get_recent_articles(
    topic: str | None = None,
    limit: int = 30,
):
    """
    Return recently used articles.

    Used by the content pipeline to avoid
    repeating titles, links and sources.
    """

    history = list_history()

    if topic:
        history = [
            item
            for item in history
            if item.get("topic") == topic
        ]

    return history[:limit]


def get_recent_article_titles(
    topic: str | None = None,
    limit: int = 30,
):
    articles = get_recent_articles(
        topic=topic,
        limit=limit,
    )

    return {
        str(item.get("title", ""))
        .strip()
        .lower()
        for item in articles
        if item.get("title")
    }


def get_recent_article_links(
    topic: str | None = None,
    limit: int = 30,
):
    articles = get_recent_articles(
        topic=topic,
        limit=limit,
    )

    return {
        str(item.get("link", ""))
        .strip()
        for item in articles
        if item.get("link")
    }


def get_last_used_source(
    topic: str,
):
    articles = get_recent_articles(
        topic=topic,
        limit=1,
    )

    if not articles:
        return None

    return articles[0].get("source")