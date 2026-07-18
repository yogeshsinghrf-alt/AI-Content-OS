from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.export_service import create_package_pdf
from app.services.history_service import get_latest_history_file


router = APIRouter()


@router.get("/latest-pdf")
def download_latest_pdf():
    latest = get_latest_history_file()

    if latest is None:
        raise HTTPException(
            status_code=404,
            detail="No saved package found. Generate content first."
        )

    file_path = create_package_pdf(latest)
    path = Path(file_path)

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=path.name,
    )