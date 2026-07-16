import os
from pathlib import Path

PHOTO_STORAGE = Path("/srv/photo-data")
# PHOTO_STORAGE = Path("./storage")

WEDDING_PASSWORD = os.environ["WEDDING_PASSWORD"]
SECRET_KEY = os.environ["SECRET_KEY"]
