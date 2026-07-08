from pathlib import Path
from PIL import Image

from app.config import PHOTO_STORAGE

from pillow_heif import register_heif_opener

register_heif_opener()

THUMBNAIL_SIZE = (300, 300)


def get_thumbnail_path(person: str, filename: str) -> Path:
    folder = PHOTO_STORAGE / ".thumbnails" / person
    folder.mkdir(parents=True, exist_ok=True)

    return folder / filename


def create_thumbnail(person: str, image_path: Path) -> Path:
    thumbnail_path = get_thumbnail_path(person, image_path.name)

    if thumbnail_path.exists():
        return thumbnail_path

    with Image.open(image_path) as image:
        image.thumbnail(THUMBNAIL_SIZE)

        image.save(thumbnail_path, "JPEG")

    return thumbnail_path
