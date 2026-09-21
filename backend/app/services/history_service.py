from app.services.r2_service import (
    delete_r2_object,
    get_json_object,
    list_r2_keys,
)


HISTORY_PREFIX = "history/"

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

    try:
        object_keys = list_r2_keys(
            HISTORY_PREFIX
        )

    except Exception as error:
        print(
            "Could not list R2 history: "
            f"{error}"
        )
        return files

    for object_key in sorted(
        object_keys,
        reverse=True,
    ):
        if not object_key.endswith(
            ".json"
        ):
            continue

        try:
            data = get_json_object(
                object_key
            )

        except Exception as error:
            print(
                "Skipping unreadable R2 "
                f"history object "
                f"{object_key}: {error}"
            )
            continue

        if not isinstance(
            data,
            dict,
        ):
            continue

        filename = object_key.rsplit(
            "/",
            1,
        )[-1]

        files.append(
            {
                "filename": filename,
                "topic": data.get(
                    "topic"
                ),
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
    if (
        not filename
        or not filename.endswith(".json")
        or "/" in filename
        or "\\" in filename
    ):
        return None

    object_key = (
        f"{HISTORY_PREFIX}{filename}"
    )

    try:
        return get_json_object(
            object_key
        )

    except Exception as error:
        print(
            "Could not read R2 history "
            f"{filename}: {error}"
        )

        return None


def delete_history_file(
    filename: str,
):
    if (
        not filename
        or not filename.endswith(".json")
        or "/" in filename
        or "\\" in filename
    ):
        return False

    object_key = (
        f"{HISTORY_PREFIX}{filename}"
    )

    try:
        existing = get_json_object(
            object_key
        )

        if not isinstance(
            existing,
            dict,
        ):
            return False

        package_id = str(
            existing.get(
                "package_id",
                "",
            )
        ).strip()

        # Delete all generated assets
        # belonging to this package first.
        if package_id:
            asset_prefix = (
                "generated-images/"
                f"{package_id}/"
            )

            asset_keys = list_r2_keys(
                asset_prefix
            )

            for asset_key in asset_keys:
                delete_r2_object(
                    asset_key
                )

        # Delete the package history JSON last.
        delete_r2_object(
            object_key
        )

        return True

    except Exception as error:
        print(
            "Could not delete R2 "
            f"history package "
            f"{filename}: {error}"
        )

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