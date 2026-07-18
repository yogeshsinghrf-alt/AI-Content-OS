from fastapi import APIRouter
from app.services.history_service import (
    list_history,
    get_history_file,
    delete_history_file
)

router = APIRouter()


@router.get("/")
def get_history():
    return list_history()


@router.get("/{filename}")
def get_history_item(filename: str):
    data = get_history_file(filename)

    if data is None:
        return {
            "status": "error",
            "message": "History file not found"
        }

    return data


@router.delete("/{filename}")
def delete_history(filename: str):
    success = delete_history_file(filename)

    if success:
        return {"status": "success"}

    return {"status": "error"}