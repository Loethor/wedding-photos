from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    File,
    Form,
    HTTPException,
)

from app.config import MAX_UPLOAD_SIZE
from app.services.storage import save_file
from app.services.thumbnails import create_thumbnail
from app.logger import logger
from app.web import templates

router = APIRouter()


@router.post("/upload")
async def upload(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    files: list[UploadFile] = File(...),
):
    username = f"{first_name}_{last_name}"
    uploaded = []

    logger.info(
        "Upload started: user=%s files=%d",
        username,
        len(files),
    )

    for file in files:
        logger.info(
            "Processing file: %s",
            file.filename,
        )

        try:
            saved, size = save_file(
                username,
                file.filename,
                file.file,
                MAX_UPLOAD_SIZE,
            )

        except ValueError:
            logger.warning(
                "Upload rejected: %s too large",
                file.filename,
            )

            raise HTTPException(
                status_code=413,
                detail=f"{file.filename} is too large",
            )

        logger.info(
            "Saved %s (%.2f MB)",
            saved,
            size / 1024 / 1024,
        )

        create_thumbnail(
            username,
            saved,
        )

        uploaded.append(saved.name)

    logger.info(
        "Upload completed: user=%s files=%d",
        username,
        len(uploaded),
    )

    return templates.TemplateResponse(
        request=request,
        name="upload_success.html",
        context={
            "count": len(uploaded),
            "files": uploaded,
        },
    )
