from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import PHOTO_STORAGE
from app.services.security import safe_path
from app.services.thumbnails import regenerate_thumbnail


router = APIRouter()

VIDEO_MEDIA_TYPES = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".m4v": "video/x-m4v",
}


def validate_file(file, error_message: str):

    if not safe_path(file):
        raise HTTPException(
            status_code=400,
            detail="errors.invalid_path",
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
        "errors.file_not_found",
    )

    return FileResponse(file)


@router.get("/video/{person}/{filename}")
def serve_video(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    validate_file(
        file,
        "errors.video_not_found",
    )

    return FileResponse(
        file,
        media_type=VIDEO_MEDIA_TYPES.get(file.suffix.lower(), "video/mp4"),
    )


@router.get("/download/{person}/{filename}")
def download_file(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    validate_file(
        file,
        "errors.file_not_found",
    )

    return FileResponse(
        file,
        filename=file.name,
    )


@router.get("/thumbnail/{person}/{filename}")
def serve_thumbnail(person: str, filename: str):

    file = PHOTO_STORAGE / ".thumbnails" / person / filename

    if not safe_path(file):
        raise HTTPException(
            status_code=400,
            detail="errors.invalid_path",
        )

    # Si la miniatura no existe (p. ej. falló al subir), intentar regenerarla.
    if not file.exists():
        regenerate_thumbnail(person, Path(filename).stem)

    if not file.exists():
        raise HTTPException(
            status_code=404,
            detail="errors.thumbnail_not_found",
        )

    return FileResponse(file)
