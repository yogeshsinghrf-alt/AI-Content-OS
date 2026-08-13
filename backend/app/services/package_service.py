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


def find_package_file(
    package_id: str,
):
    """
    Find the history JSON file belonging
    to a specific package_id.
    """

    if not package_id:
        return None

    if not HISTORY_DIR.exists():
        return None

    for file_path in HISTORY_DIR.glob(
        "*.json"
    ):
        try:
            with file_path.open(
                "r",
                encoding="utf-8",
            ) as f:
                data = json.load(f)

        except (
            json.JSONDecodeError,
            OSError,
        ):
            continue

        if (
            data.get("package_id")
            == package_id
        ):
            return file_path

    return None
def get_package_by_id(
    package_id: str,
):
    """
    Load the complete saved package
    belonging to a specific package_id.
    """

    file_path = find_package_file(
        package_id
    )

    if file_path is None:
        return None

    try:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except (
        json.JSONDecodeError,
        OSError,
    ) as error:
        print(
            f"Could not load package "
            f"{package_id}: {error}"
        )

        return None

def update_package_asset(
    package_id: str,
    platform: str,
    asset: dict,
):
    """
    Attach one generated visual asset to
    the correct saved content package.
    """

    file_path = find_package_file(
        package_id
    )

    if file_path is None:
        return False

    try:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        assets = data.get(
            "assets",
            {},
        )

        if not isinstance(
            assets,
            dict,
        ):
            assets = {}

        if platform == "carousel":
            carousel_assets = assets.get(
                "carousel",
                [],
            )

            if not isinstance(
                carousel_assets,
                list,
            ):
                carousel_assets = []

            carousel_assets.append(
                asset
            )

            assets["carousel"] = (
                carousel_assets
            )

        else:
            assets[platform] = asset

        data["assets"] = assets

        

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False,
            )

        return True

    except (
        json.JSONDecodeError,
        OSError,
    ) as error:
        print(
            f"Could not update package assets "
            f"for {package_id}: {error}"
        )

        return False