from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import PHOTO_STORAGE
from app.services.security import safe_path


router = APIRouter()


def validate_file(file, error_message: str):

    if not safe_path(file):
        raise HTTPException(
            status_code=400,
            detail="Invalid path",
        )

    if not file.exists():
        raise HTTPException(
            status_code=404,
            detail=error_message,
        )


@router.get("/photo/{person}/{filename}")
def serve_photo(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    validate_file(
        file,
        "File not found",
    )

    return FileResponse(file)


@router.get("/video/{person}/{filename}")
def serve_video(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    validate_file(
        file,
        "Video not found",
    )

    return FileResponse(
        file,
        media_type="video/mp4",
    )


@router.get("/download/{person}/{filename}")
def download_file(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    validate_file(
        file,
        "File not found",
    )

    return FileResponse(
        file,
        filename=file.name,
    )


@router.get("/thumbnail/{person}/{filename}")
def serve_thumbnail(person: str, filename: str):

    file = PHOTO_STORAGE / ".thumbnails" / person / filename

    validate_file(
        file,
        "Thumbnail not found",
    )

    return FileResponse(file)
