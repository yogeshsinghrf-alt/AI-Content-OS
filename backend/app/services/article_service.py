import re

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


def clean_text(text: str) -> str:
    """
    Normalize whitespace while preserving readable paragraphs.
    """

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text,
    )

    return text.strip()


def fetch_article_text(
    url: str,
    max_chars: int = 12000,
) -> str:
    """
    Download an article and extract useful readable text.

    Returns an empty string if extraction fails so the
    content pipeline can continue safely.
    """

    if not url:
        return ""

    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=20,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Remove content that should never be sent
        # to the language model.
        for tag in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
                "noscript",
                "svg",
            ]
        ):
            tag.decompose()

        # Prefer the actual article container.
        article = soup.find("article")

        if article:
            container = article
        else:
            container = soup.find("main")

        if container is None:
            container = soup.body

        if container is None:
            return ""

        paragraphs = []

        for element in container.find_all(
            [
                "p",
                "h2",
                "h3",
                "li",
            ]
        ):
            text = element.get_text(
                " ",
                strip=True,
            )

            # Ignore tiny fragments/navigation remnants.
            if len(text) < 40:
                continue

            paragraphs.append(text)

        article_text = "\n\n".join(
            paragraphs
        )

        article_text = clean_text(
            article_text
        )

        if len(article_text) > max_chars:
            article_text = (
                article_text[:max_chars]
                + "\n\n[Article text truncated]"
            )

        return article_text

    except requests.RequestException as error:
        print(
            f"Could not fetch article "
            f"{url}: {error}"
        )
        return ""

    except Exception as error:
        print(
            f"Could not extract article "
            f"{url}: {error}"
        )
        return ""