import json
from datetime import datetime


def save_package(response: dict, topic: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"history/{timestamp}_{topic}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2, ensure_ascii=False)

    return filename