import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
HISTORY_DIR = BASE_DIR / "history"


def save_package(
    response: dict,
    topic: str,
):
    """
    Save a generated content package
    to the backend history directory.
    """

    HISTORY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = (
        f"{timestamp}_{topic}.json"
    )

    file_path = (
        HISTORY_DIR / filename
    )

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            response,
            f,
            indent=2,
            ensure_ascii=False,
        )

    return str(file_path)