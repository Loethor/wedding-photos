from pathlib import Path

from app.config import PHOTO_STORAGE


def safe_path(path: Path) -> bool:
    try:
        path.resolve().relative_to(PHOTO_STORAGE.resolve())
        return True

    except ValueError:
        return False
