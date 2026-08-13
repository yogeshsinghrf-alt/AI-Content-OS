from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


HTML_SOURCES = {
    "ai": [
        {
            "name": "Anthropic",
            "url": "https://www.anthropic.com/news",
            "allowed_domains": [
                "anthropic.com",
                "www.anthropic.com",
            ],
            "required_path_parts": [
                "/news/",
            ],
        },
        {
            "name": "Google DeepMind",
            "url": "https://deepmind.google/blog/",
            "allowed_domains": [
                "deepmind.google",
            ],
            "required_path_parts": [
                "/blog/",
            ],
        },
        {
            "name": "Microsoft AI",
            "url": "https://blogs.microsoft.com/",
            "allowed_domains": [
                "blogs.microsoft.com",
            ],
            "required_path_parts": [
                "/blog/",
                "/ai/",
                "/ai-for-business/",
            ],
        },
        {
            "name": "Meta AI",
            "url": "https://ai.meta.com/blog/",
            "allowed_domains": [
                "ai.meta.com",
            ],
            "required_path_parts": [
                "/blog/",
            ],
        },
        {
            "name": "World Economic Forum AI",
            "url": (
                "https://www.weforum.org/stories/"
                "artificial-intelligence/"
            ),
            "allowed_domains": [
                "weforum.org",
                "www.weforum.org",
            ],
            "required_path_parts": [
                "/stories/",
                "/publications/",
            ],
        },
    ],
}


def _is_allowed_article_link(
    url: str,
    allowed_domains: list[str],
    required_path_parts: list[str],
) -> bool:
    parsed = urlparse(url)

    domain = parsed.netloc.lower()

    if domain not in allowed_domains:
        return False

    path = parsed.path.lower()

    if not any(
        part.lower() in path
        for part in required_path_parts
    ):
        return False

    blocked_parts = [
        "/about",
        "/careers",
        "/contact",
        "/privacy",
        "/terms",
        "/events",
        "/newsletter",
        "/author/",
        "/tag/",
        "/category/",
    ]

    if any(
        blocked in path
        for blocked in blocked_parts
    ):
        return False

    return True


def discover_html_articles(
    source_name: str,
    page_url: str,
    allowed_domains: list[str],
    required_path_parts: list[str],
    limit: int = 5,
):
    """
    Discover recent-looking article links from a
    publisher's news/index page.

    Returns records compatible with package.py.
    """

    try:
        response = requests.get(
            page_url,
            headers=DEFAULT_HEADERS,
            timeout=20,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(
            f"Could not discover {source_name}: "
            f"{error}"
        )

        return []

    try:
        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        articles = []
        seen_links = set()
        seen_titles = set()

        for anchor in soup.find_all(
            "a",
            href=True,
        ):
            href = str(
                anchor.get("href", "")
            ).strip()

            title = anchor.get_text(
                " ",
                strip=True,
            )

            if not href or not title:
                continue

            # Ignore tiny menu/navigation labels.
            if len(title) < 15:
                continue

            absolute_url = urljoin(
                page_url,
                href,
            )

            if not _is_allowed_article_link(
                absolute_url,
                allowed_domains,
                required_path_parts,
            ):
                continue

            normalized_link = (
                absolute_url
                .split("#")[0]
                .rstrip("/")
            )

            normalized_title = (
                title
                .strip()
                .lower()
            )

            if normalized_link in seen_links:
                continue

            if normalized_title in seen_titles:
                continue

            seen_links.add(
                normalized_link
            )

            seen_titles.add(
                normalized_title
            )

            articles.append(
                {
                    "source": source_name,
                    "title": title.strip(),
                    "link": normalized_link,
                    "published_timestamp": None,
                }
            )

            if len(articles) >= limit:
                break

        return articles

    except Exception as error:
        print(
            f"Could not parse discovery page "
            f"for {source_name}: {error}"
        )

        return []


def discover_topic_articles(
    topic: str,
    limit_per_source: int = 5,
):
    """
    Discover articles from configured HTML sources
    for a topic.
    """

    sources = HTML_SOURCES.get(
        topic,
        [],
    )

    discovered = []

    for source in sources:
        articles = discover_html_articles(
            source_name=source["name"],
            page_url=source["url"],
            allowed_domains=source[
                "allowed_domains"
            ],
            required_path_parts=source[
                "required_path_parts"
            ],
            limit=limit_per_source,
        )

        discovered.extend(
            articles
        )

    return discovered