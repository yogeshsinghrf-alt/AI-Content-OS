from datetime import datetime
import threading

from app.services.r2_service import (
    get_json_object,
    list_r2_keys,
    put_json_object,
)


HISTORY_PREFIX = "history/"

# Current Render deployment is one application instance.
# This prevents parallel image requests from overwriting
# each other's asset metadata during R2 read/modify/write.
_package_update_lock = threading.Lock()


def _safe_topic(topic: str):
    value = "".join(
        char
        if char.isalnum()
        or char in ("-", "_")
        else "_"
        for char in str(topic)
    )

    return value or "general"


def save_package(
    response: dict,
    topic: str,
):
    """
    Persist a generated content package
    in Cloudflare R2.
    """

    package_id = str(
        response.get(
            "package_id",
            "",
        )
    ).strip()

    if not package_id:
        package_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

    filename = (
        f"{package_id}_"
        f"{_safe_topic(topic)}.json"
    )

    object_key = (
        f"{HISTORY_PREFIX}{filename}"
    )

    put_json_object(
        object_key,
        response,
    )

    return object_key


def find_package_file(
    package_id: str,
):
    """
    Find the R2 history object belonging
    to a specific package_id.
    """

    if not package_id:
        return None

    keys = list_r2_keys(
        f"{HISTORY_PREFIX}{package_id}"
    )

    for object_key in keys:
        try:
            data = get_json_object(
                object_key
            )

        except Exception as error:
            print(
                "Could not read package "
                f"{object_key}: {error}"
            )
            continue

        if (
            isinstance(data, dict)
            and data.get("package_id")
            == package_id
        ):
            return object_key

    return None


def get_package_by_id(
    package_id: str,
):
    """
    Load a complete package from R2.
    """

    object_key = find_package_file(
        package_id
    )

    if object_key is None:
        return None

    try:
        return get_json_object(
            object_key
        )

    except Exception as error:
        print(
            "Could not load package "
            f"{package_id}: {error}"
        )
        return None


def update_package_asset(
    package_id: str,
    platform: str,
    asset: dict,
):
    """
    Attach generated asset metadata
    to the correct package in R2.
    """

    with _package_update_lock:
        object_key = find_package_file(
            package_id
        )

        if object_key is None:
            return False

        try:
            data = get_json_object(
                object_key
            )

            if not isinstance(
                data,
                dict,
            ):
                return False

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
                carousel_assets = (
                    assets.get(
                        "carousel",
                        [],
                    )
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

            put_json_object(
                object_key,
                data,
            )

            return True

        except Exception as error:
            print(
                "Could not update package "
                f"assets for {package_id}: "
                f"{error}"
            )

            return False