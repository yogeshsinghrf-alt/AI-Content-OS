import json
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
HISTORY_DIR = BASE_DIR / "history"

def _extract_articles_from_package(
    data: dict,
):
    """
    Return every source article stored in a package.

    Supports:
    - new multi-story packages
    - older single-story history files
    """

    articles = []

    stories = data.get(
        "stories",
        [],
    )

    if isinstance(stories, list):
        for story in stories:
            if not isinstance(
                story,
                dict,
            ):
                continue

            title = str(
                story.get(
                    "title",
                    "",
                )
            ).strip()

            link = str(
                story.get(
                    "link",
                    "",
                )
            ).strip()

            source = str(
                story.get(
                    "source",
                    "",
                )
            ).strip()

            if not title and not link:
                continue

            articles.append(
                {
                    "title": title,
                    "link": link,
                    "source": source,
                    "slot": story.get(
                        "slot"
                    ),
                }
            )

    # Backward compatibility with
    # existing Phase-1 history files.
    if not articles:
        title = str(
            data.get(
                "article_title",
                "",
            )
        ).strip()

        link = str(
            data.get(
                "article_link",
                "",
            )
        ).strip()

        source = str(
            data.get(
                "source",
                "",
            )
        ).strip()

        if title or link:
            articles.append(
                {
                    "title": title,
                    "link": link,
                    "source": source,
                    "slot": None,
                }
            )

    return articles

def list_history():
    files = []

    if not HISTORY_DIR.exists():
        return files

    for filename in sorted(
        os.listdir(HISTORY_DIR),
        reverse=True,
    ):
        if not filename.endswith(".json"):
            continue

        file_path = HISTORY_DIR / filename

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as f:
                data = json.load(f)

        except (
            json.JSONDecodeError,
            OSError,
        ) as error:
            print(
                f"Skipping unreadable history file "
                f"{filename}: {error}"
            )
            continue

        files.append(
            {
                "filename": filename,
                "topic": data.get("topic"),
                "title": data.get(
                    "article_title"
                ),
                "link": data.get(
                    "article_link"
                ),
                "source": data.get(
                    "source"
                ),
            }
        )

    return files


def get_history_file(
    filename: str,
):
    file_path = HISTORY_DIR / filename

    if not file_path.exists():
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
    ) as error:
        print(
            f"Skipping unreadable history file "
            f"{filename}: {error}"
        )
        return None


def delete_history_file(
    filename: str,
):
    file_path = HISTORY_DIR / filename

    if file_path.exists():
        try:
            file_path.unlink()
            return True

        except OSError as error:
            print(
                f"Could not delete history file "
                f"{filename}: {error}"
            )
            return False

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
    Return recently used source articles.

    Multi-story packages are flattened so every
    article participates in duplicate protection.
    Older single-story packages remain supported.
    """

    history = list_history()

    recent_articles = []

    for history_item in history:
        if (
            topic
            and history_item.get(
                "topic"
            ) != topic
        ):
            continue

        filename = history_item.get(
            "filename"
        )

        if not filename:
            continue

        package = get_history_file(
            filename
        )

        if not isinstance(
            package,
            dict,
        ):
            continue

        package_articles = (
            _extract_articles_from_package(
                package
            )
        )

        for article in package_articles:
            recent_articles.append(
                article
            )

            if (
                len(recent_articles)
                >= limit
            ):
                return recent_articles

    return recent_articles


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

    return articles[0].get(
        "source"
    )