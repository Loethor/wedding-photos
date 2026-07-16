from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.config import PHOTO_STORAGE
from app.services.security import safe_path


router = APIRouter()


@router.get("/photo/{person}/{filename}")
def serve_photo(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    if not safe_path(file):
        return {"error": "Invalid path"}

    if not file.exists():
        return {"error": "File not found"}

    return FileResponse(file)


@router.get("/video/{person}/{filename}")
def serve_video(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    if not safe_path(file):
        return {"error": "Invalid path"}

    if not file.exists():
        return {"error": "Video not found"}

    return FileResponse(
        file,
        media_type="video/mp4",
    )


@router.get("/download/{person}/{filename}")
def download_file(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    if not safe_path(file):
        return {"error": "Invalid path"}

    if not file.exists():
        return {"error": "File not found"}

    return FileResponse(
        file,
        filename=file.name,
    )


@router.get("/thumbnail/{person}/{filename}")
def serve_thumbnail(person: str, filename: str):

    file = PHOTO_STORAGE / ".thumbnails" / person / filename

    if not safe_path(file):
        return {"error": "Invalid path"}

    if not file.exists():
        return {"error": "Thumbnail not found"}

    return FileResponse(file)
