from pathlib import Path
import subprocess

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

from app.config import PHOTO_STORAGE
from app.services.storage import (
    ALLOWED_EXTENSIONS,
    HEIF_EXTENSIONS,
    VIDEO_EXTENSIONS,
    list_people,
    unique_path,
)

register_heif_opener()

# Miniaturas a 600px para que se vean nítidas en pantallas retina/móviles
# (las celdas de la galería ocupan más píxeles físicos de los que parece).
THUMBNAIL_SIZE = (600, 600)


def convert_heif_to_jpeg(file_path: Path) -> Path:
    """Convierte un HEIC/HEIF a JPEG para que se vea en cualquier navegador.

    Devuelve la ruta del JPEG resultante (y borra el original). Si el archivo
    no es HEIF, lo devuelve tal cual.
    """
    if file_path.suffix.lower() not in HEIF_EXTENSIONS:
        return file_path

    target = unique_path(file_path.parent, f"{file_path.stem}.jpg")

    with Image.open(file_path) as image:
        fixed = ImageOps.exif_transpose(image) or image  # orientación del móvil
        fixed.convert("RGB").save(target, "JPEG", quality=90)

    file_path.unlink(missing_ok=True)
    return target


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
        fixed = ImageOps.exif_transpose(image) or image  # orientación del móvil
        fixed.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)  # mejor reducción

        fixed.convert("RGB").save(
            thumbnail_path,
            "JPEG",
            quality=85,
            optimize=True,
        )


def regenerate_thumbnail(person: str, stem: str) -> Path | None:
    """Regenera la miniatura buscando el original por su nombre (sin extensión).

    Se usa como red de seguridad si la miniatura falta (p. ej. falló al subir).
    Devuelve la ruta de la miniatura o None si no hay original válido.
    """
    if person not in list_people():  # evita path traversal vía {person}
        return None

    folder = PHOTO_STORAGE / person
    for file in folder.iterdir():
        if file.stem == stem and file.suffix.lower() in ALLOWED_EXTENSIONS:
            try:
                return create_thumbnail(person, file)
            except Exception:
                return None

    return None


def create_video_thumbnail(
    video_path: Path,
    thumbnail_path: Path,
):
    width, height = THUMBNAIL_SIZE
    # Ajustar a la caja de la miniatura sin ampliar vídeos pequeños.
    scale = (
        f"scale='min({width},iw)':'min({height},ih)':"
        "force_original_aspect_ratio=decrease"
    )

    # Intentamos el frame del segundo 1; si el vídeo dura menos, ffmpeg no encuentra
    # frame y falla, así que caemos al inicio (segundo 0) antes de darnos por vencidos.
    last_error: subprocess.CalledProcessError | None = None
    for seek in ("00:00:01", "00:00:00"):
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-ss",
                    seek,
                    "-i",
                    str(video_path),
                    "-frames:v",
                    "1",
                    "-vf",
                    scale,
                    str(thumbnail_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except subprocess.CalledProcessError as exc:
            last_error = exc

    # El bucle siempre se ejecuta, así que si llegamos aquí hubo al menos un error.
    assert last_error is not None
    raise last_error
