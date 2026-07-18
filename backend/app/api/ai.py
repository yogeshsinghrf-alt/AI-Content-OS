from fastapi import APIRouter
from app.ai.gemini_service import generate_summary

router = APIRouter()


@router.get("/summary")
def summary():

    text = """
    NVIDIA has released new AI fine tuning tools
    for enterprise models.
    """

    result = generate_summary(text)

    return {
        "summary": result
    }