from fastapi import (
    APIRouter,
    HTTPException,
)

from app.services.r2_service import (
    test_r2_round_trip,
)


router = APIRouter()


@router.post("/test")
def test_storage():
    try:
        return test_r2_round_trip()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "R2 storage test failed: "
                f"{type(error).__name__}: "
                f"{error}"
            ),
        )