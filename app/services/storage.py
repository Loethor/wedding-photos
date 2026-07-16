from pathlib import Path
import unicodedata
import re
from app.config import PHOTO_STORAGE


def get_user_folder(username: str) -> Path:
    safe_name = sanitize_folder_name(username)

    folder = PHOTO_STORAGE / safe_name

    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_file(username: str, filename: str, content: bytes) -> Path:
    folder = get_user_folder(username)

    target = folder / filename

    # Evitar sobrescribir
    counter = 1
    while target.exists():
        target = folder / f"{target.stem}_{counter}{target.suffix}"
        counter += 1

    target.write_bytes(content)

    return target


def sanitize_folder_name(value: str) -> str:
    # Quitar acentos
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )

    # Sustituir espacios y caracteres raros
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value)

    # Quitar guiones bajos sobrantes
    return value.strip("_")


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".heic",
    ".heif",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".avi",
}

ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def list_people() -> list[str]:
    if not PHOTO_STORAGE.exists():
        return []

    return sorted(
        [
            folder.name
            for folder in PHOTO_STORAGE.iterdir()
            if folder.is_dir() and not folder.name.startswith(".")
        ]
    )


def list_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []

    return sorted(
        [file for file in folder.iterdir() if file.suffix.lower() in ALLOWED_EXTENSIONS]
    )


def get_all_files() -> list[tuple[str, Path]]:
    result = []

    for person in list_people():
        folder = PHOTO_STORAGE / person

        for file in list_files(folder):
            result.append((person, file))

    return result
