from pathlib import Path
import subprocess

from PIL import Image
from pillow_heif import register_heif_opener

from app.config import PHOTO_STORAGE
from app.services.storage import VIDEO_EXTENSIONS

register_heif_opener()

THUMBNAIL_SIZE = (300, 300)


def get_thumbnail_path(person: str, filename: str) -> Path:
    folder = PHOTO_STORAGE / ".thumbnails" / person
    folder.mkdir(parents=True, exist_ok=True)

    # Siempre generamos jpg para thumbnails
    return folder / f"{Path(filename).stem}.jpg"


def create_thumbnail(person: str, file_path: Path) -> Path:
    thumbnail_path = get_thumbnail_path(person, file_path.name)

    if thumbnail_path.exists():
        return thumbnail_path

    if file_path.suffix.lower() in VIDEO_EXTENSIONS:
        create_video_thumbnail(file_path, thumbnail_path)
    else:
        create_image_thumbnail(file_path, thumbnail_path)

    return thumbnail_path


def create_image_thumbnail(
    image_path: Path,
    thumbnail_path: Path,
):
    with Image.open(image_path) as image:
        image.thumbnail(THUMBNAIL_SIZE)

        image.convert("RGB").save(
            thumbnail_path,
            "JPEG",
        )


def create_video_thumbnail(
    video_path: Path,
    thumbnail_path: Path,
):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-ss",
            "00:00:01",
            "-frames:v",
            "1",
            str(thumbnail_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
