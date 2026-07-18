import os
import json


def list_history():
    files = []

    if not os.path.exists("history"):
        return files

    for file in sorted(os.listdir("history"), reverse=True):
        if file.endswith(".json"):
            with open(f"history/{file}", "r", encoding="utf-8") as f:
                data = json.load(f)

            files.append({
                "filename": file,
                "topic": data.get("topic"),
                "title": data.get("article_title"),
                "source": data.get("source")
            })

    return files


def get_history_file(filename: str):
    file_path = f"history/{filename}"

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_history_file(filename: str):
    file_path = f"history/{filename}"

    if os.path.exists(file_path):
        os.remove(file_path)
        return True

    return False
def get_latest_history_file():
    files = list_history()

    if not files:
        return None

    latest = files[0]

    return get_history_file(latest["filename"])