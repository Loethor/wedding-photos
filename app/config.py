import os
from pathlib import Path

PHOTO_STORAGE = Path("/srv/photo-data/wedding-photos")
# PHOTO_STORAGE = Path("./storage")

WEDDING_PASSWORD = os.environ["WEDDING_PASSWORD"]
SECRET_KEY = os.environ["SECRET_KEY"]

MAX_UPLOAD_SIZE = 1024 * 1024 * 1024  # 1 GB
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MB
