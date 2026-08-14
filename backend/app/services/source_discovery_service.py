import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


HTML_SOURCES = {
    "ai": [
        {
            "name": "Anthropic",
            "url": "https://www.anthropic.com/news",
            "allowed_domains": {
                "anthropic.com",
                "www.anthropic.com",
            },
            "article_path_regex": r"^/news/[^/]+/?$",
            "blocked_paths": {"/news"},
        },
        {
            "name": "Google DeepMind",
            "url": "https://deepmind.google/blog/",
            "allowed_domains": {"deepmind.google"},
            "article_path_regex": r"^/blog/[^/]+/?$",
            "blocked_paths": {"/blog"},
        },
        {
            "name": "Microsoft AI",
            "url": "https://blogs.microsoft.com/",
            "allowed_domains": {"blogs.microsoft.com"},
            "article_path_regex": r"^/blog/\d{4}/\d{2}/\d{2}/[^/]+/?$",
            "blocked_paths": {
                "/",
                "/blog",
                "/ai",
                "/ai-for-business",
            },
        },
        {
            "name": "Meta AI",
            "url": "https://ai.meta.com/blog/",
            "allowed_domains": {"ai.meta.com"},
            "article_path_regex": r"^/blog/[^/]+/?$",
            "blocked_paths": {"/blog"},
        },
        {
            "name": "World Economic Forum AI",
            "url": (
                "https://www.weforum.org/stories/"
                "artificial-intelligence/"
            ),
            "allowed_domains": {
                "weforum.org",
                "www.weforum.org",
            },
            "article_path_regex": (
                r"^/stories/artificial-intelligence/"
                r"[^/]+/?$"
            ),
            "blocked_paths": {
                "/stories/artificial-intelligence"
            },
        },
    ],
}


GENERIC_TITLES = {
    "about",
    "ai",
    "artificial intelligence",
    "articles",
    "blog",
    "blogs",
    "discover",
    "explore",
    "featured",
    "home",
    "homepage",
    "insights",
    "latest",
    "latest news",
    "learn more",
    "more",
    "news",
    "next",
    "previous",
    "read",
    "read more",
    "research",
    "see all",
    "skip to content",
    "skip to main content",
    "stories",
    "technology",
    "view all",
}


BLOCKED_TITLE_FRAGMENTS = (
    "cookie policy",
    "privacy policy",
    "skip to content",
    "skip to main",
    "terms of use",
)


def _normalize_path(path: str) -> str:
    normalized = path.strip().lower().rstrip("/")
    return normalized or "/"


def _normalize_title(title: str) -> str:
    return " ".join(str(title).split()).strip()


def _is_useful_title(title: str) -> bool:
    normalized = _normalize_title(title)

    if not normalized:
        return False

    lowered = normalized.lower()

    if lowered in GENERIC_TITLES:
        return False

    if any(
        fragment in lowered
        for fragment in BLOCKED_TITLE_FRAGMENTS
    ):
        return False

    if len(normalized) < 12:
        return False

    if len(normalized.split()) < 2:
        return False

    return True


def _extract_anchor_title(anchor) -> str:
    """
    Prefer semantic heading text inside a card/link.
    Fall back to accessibility/title attributes and,
    finally, visible anchor text.
    """

    heading = anchor.find(
        ["h1", "h2", "h3", "h4"]
    )

    candidates = []

    if heading is not None:
        candidates.append(
            heading.get_text(" ", strip=True)
        )

    aria_label = anchor.get("aria-label")

    if aria_label:
        candidates.append(str(aria_label))

    title_attr = anchor.get("title")

    if title_attr:
        candidates.append(str(title_attr))

    candidates.append(
        anchor.get_text(" ", strip=True)
    )

    for candidate in candidates:
        candidate = _normalize_title(candidate)

        if _is_useful_title(candidate):
            return candidate

    return ""


def _is_allowed_article_link(
    url: str,
    source: dict,
) -> bool:
    parsed = urlparse(url)

    domain = parsed.netloc.lower()

    if domain not in source["allowed_domains"]:
        return False

    path = _normalize_path(parsed.path)

    blocked_paths = {
        _normalize_path(item)
        for item in source.get(
            "blocked_paths",
            set(),
        )
    }

    if path in blocked_paths:
        return False

    blocked_path_parts = (
        "/about",
        "/author/",
        "/careers",
        "/category/",
        "/contact",
        "/events",
        "/newsletter",
        "/privacy",
        "/search",
        "/tag/",
        "/terms",
    )

    if any(
        part in path
        for part in blocked_path_parts
    ):
        return False

    article_regex = source.get(
        "article_path_regex"
    )

    if article_regex and not re.match(
        article_regex,
        parsed.path,
        flags=re.IGNORECASE,
    ):
        return False

    return True


def _discover_source_articles(
    source: dict,
    limit: int = 5,
):
    source_name = source["name"]
    page_url = source["url"]

    try:
        response = requests.get(
            page_url,
            headers={
                **DEFAULT_HEADERS,
                "Referer": page_url,
            },
            timeout=20,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(
            f"Could not discover "
            f"{source_name}: {error}"
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

            if not href:
                continue

            absolute_url = urljoin(
                page_url,
                href,
            )

            if not _is_allowed_article_link(
                absolute_url,
                source,
            ):
                continue

            title = _extract_anchor_title(
                anchor
            )

            if not title:
                continue

            normalized_link = (
                absolute_url
                .split("#", 1)[0]
                .split("?", 1)[0]
                .rstrip("/")
            )

            normalized_title = (
                _normalize_title(title)
                .lower()
            )

            if normalized_link in seen_links:
                continue

            if normalized_title in seen_titles:
                continue

            seen_links.add(normalized_link)
            seen_titles.add(normalized_title)

            articles.append(
                {
                    "source": source_name,
                    "title": title,
                    "link": normalized_link,
                    "published_timestamp": None,
                }
            )

            if len(articles) >= limit:
                break

        if not articles:
            print(
                f"No usable article links "
                f"discovered for {source_name}."
            )

        return articles

    except Exception as error:
        print(
            f"Could not parse discovery page "
            f"for {source_name}: {error}"
        )

        return []


def discover_html_articles(
    source_name: str,
    page_url: str,
    allowed_domains: list[str],
    required_path_parts: list[str],
    limit: int = 5,
):
    """
    Backward-compatible wrapper for older callers.

    New code should use discover_topic_articles(), which
    applies the stricter source-specific configuration.
    """

    source = {
        "name": source_name,
        "url": page_url,
        "allowed_domains": set(
            allowed_domains
        ),
        "blocked_paths": set(),
    }

    if required_path_parts:
        escaped_parts = [
            re.escape(
                part.rstrip("/")
            )
            for part in required_path_parts
        ]

        source["article_path_regex"] = (
            r"^(?:"
            + "|".join(
                f"{part}/.+"
                for part in escaped_parts
            )
            + r")/?$"
        )

    return _discover_source_articles(
        source=source,
        limit=limit,
    )


def discover_topic_articles(
    topic: str,
    limit_per_source: int = 5,
):
    """
    Discover article-level links from configured HTML
    publishers for a topic.

    A failure from one publisher never prevents the other
    publishers from contributing candidates.
    """

    sources = HTML_SOURCES.get(
        topic,
        [],
    )

    discovered = []

    for source in sources:
        articles = _discover_source_articles(
            source=source,
            limit=limit_per_source,
        )

        discovered.extend(articles)

    return discovered
