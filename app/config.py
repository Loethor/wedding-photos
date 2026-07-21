import os
from pathlib import Path

PHOTO_STORAGE = Path("/srv/photo-data/wedding-photos")
# PHOTO_STORAGE = Path("./storage")

WEDDING_PASSWORD = os.environ["WEDDING_PASSWORD"]
SECRET_KEY = os.environ["SECRET_KEY"]

MAX_UPLOAD_SIZE = 1024 * 1024 * 1024  # 1 GB
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MB
SESSION_MAX_AGE = 60 * 60 * 24 * 30

# La cookie de sesión lleva el flag Secure (solo se envía por HTTPS). En producción
# (nginx con TLS) debe estar activo; en desarrollo local por HTTP hay que ponerlo a
# "false" (p. ej. SECURE_COOKIES=false) o el navegador descarta la cookie y el login
# entra en un bucle de redirección.
SECURE_COOKIES = os.environ.get("SECURE_COOKIES", "true").strip().lower() not in (
    "0",
    "false",
    "no",
)
