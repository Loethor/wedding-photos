from pathlib import Path
import unicodedata
import re
from app.config import PHOTO_STORAGE, UPLOAD_CHUNK_SIZE


def get_user_folder(username: str) -> Path:
    safe_name = sanitize_folder_name(username)

    folder = PHOTO_STORAGE / safe_name

    folder.mkdir(parents=True, exist_ok=True)
    return folder


# Archivo lateral donde guardamos el nombre original (con acentos/ñ) para mostrar,
# ya que el nombre de la carpeta va sanitizado a ASCII.
DISPLAY_NAME_FILE = ".display_name"


def set_display_name(folder: Path, display: str) -> None:
    display = " ".join(display.split())[:80]  # una línea, sin espacios sobrantes
    if display:
        (folder / DISPLAY_NAME_FILE).write_text(display, encoding="utf-8")


def get_display_name(folder_name: str) -> str:
    """Nombre para mostrar: el original con acentos si existe, si no el de carpeta."""
    try:
        name = (
            (PHOTO_STORAGE / folder_name / DISPLAY_NAME_FILE)
            .read_text(encoding="utf-8")
            .strip()
        )
        if name:
            return name
    except OSError:
        pass

    return folder_name.replace("_", " ")


def unique_path(folder: Path, filename: str) -> Path:
    """Devuelve una ruta que no colisiona, añadiendo _1, _2… al nombre."""
    stem = Path(filename).stem
    suffix = Path(filename).suffix

    target = folder / filename
    counter = 1
    while target.exists():
        target = folder / f"{stem}_{counter}{suffix}"
        counter += 1

    return target


def save_file(username: str, filename: str, source, max_size: int) -> tuple[Path, int]:
    folder = get_user_folder(username)

    filename = sanitize_filename(filename)

    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("File type not allowed")

    target = unique_path(folder, filename)

    size = 0

    with target.open("wb") as f:
        while chunk := source.read(UPLOAD_CHUNK_SIZE):
            size += len(chunk)

            if size > max_size:
                target.unlink(missing_ok=True)

                raise ValueError("File too large")

            f.write(chunk)

    return target, size


def sanitize_folder_name(value: str) -> str:
    # Quitar acentos
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )

    # Sustituir espacios y caracteres raros
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value)

    # Quitar guiones bajos sobrantes
    return value.strip("_")


def sanitize_filename(value: str) -> str:
    # quitar ruta si viene incluida
    value = Path(value).name

    # normalizar unicode (HEIC/iPhone puede traer caracteres raros)
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )

    # conservar extensión
    suffix = Path(value).suffix.lower()
    stem = Path(value).stem

    stem = re.sub(r"[^a-zA-Z0-9]+", "_", stem)
    stem = stem.strip("_")

    return f"{stem}{suffix}"


# HEIC/HEIF (formato por defecto del iPhone) no se ve en navegadores que no
# sean Safari, así que estos se convierten a JPEG al subirlos.
HEIF_EXTENSIONS = {
    ".heic",
    ".heif",
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
} | HEIF_EXTENSIONS

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
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
