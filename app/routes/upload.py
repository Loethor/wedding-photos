from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    UploadFile,
    File,
    Form,
)
from starlette.concurrency import run_in_threadpool

from app.config import MAX_UPLOAD_SIZE
from app.services.storage import sanitize_folder_name, save_file, set_display_name
from app.services.thumbnails import convert_heif_to_jpeg, create_thumbnail
from app.logger import logger
from app.web import templates

router = APIRouter()


@router.post("/upload")
async def upload(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    files: list[UploadFile] = File(...),
):
    username = f"{first_name}_{last_name}"

    # El nombre debe producir una carpeta válida. Se translitera cualquier alfabeto a
    # ASCII (griego, cirílico, árabe…), así que solo queda vacío si no tiene ninguna
    # letra (p. ej. solo emojis/símbolos); en ese caso rechazamos la subida en vez de
    # dejar los archivos sueltos en la raíz del almacenamiento.
    if not sanitize_folder_name(username):
        raise HTTPException(status_code=400, detail="errors.invalid_name")

    display_name = f"{first_name.strip()} {last_name.strip()}"
    uploaded: list[str] = []
    failed: list[str] = []

    logger.info(
        "Upload started: user=%s files=%d",
        username,
        len(files),
    )

    for file in files:
        filename = file.filename
        if not filename:
            continue

        logger.info(
            "Processing file: %s",
            filename,
        )

        # Guardar en disco (en threadpool para no bloquear el event loop).
        try:
            saved, size = await run_in_threadpool(
                save_file,
                username,
                filename,
                file.file,
                MAX_UPLOAD_SIZE,
            )
        except ValueError as exc:
            # Archivo demasiado grande o tipo no permitido: lo saltamos, pero
            # no abortamos el resto de la subida.
            logger.warning(
                "Upload skipped: %s (%s)",
                filename,
                exc,
            )
            failed.append(filename)
            continue

        logger.info(
            "Saved %s (%.2f MB)",
            saved,
            size / 1024 / 1024,
        )

        # Convertir HEIC/HEIF de iPhone a JPEG (si falla, seguimos con el original).
        try:
            saved = await run_in_threadpool(convert_heif_to_jpeg, saved)
        except Exception:
            logger.exception(
                "HEIF conversion failed for %s",
                saved,
            )

        # La miniatura debe usar el nombre de carpeta ya sanitizado (el mismo que
        # usan la galería y las URLs), no el username crudo con acentos/espacios.
        person = saved.parent.name

        # Guardar el nombre original (con acentos) para mostrar en la galería.
        if not uploaded:
            set_display_name(saved.parent, display_name)

        # Generar miniatura. Si falla, no abortamos: puede regenerarse al vuelo.
        try:
            await run_in_threadpool(create_thumbnail, person, saved)
        except Exception:
            logger.exception(
                "Thumbnail failed for %s",
                saved,
            )

        uploaded.append(saved.name)

    logger.info(
        "Upload completed: user=%s uploaded=%d failed=%d",
        username,
        len(uploaded),
        len(failed),
    )

    return templates.TemplateResponse(
        request=request,
        name="upload_success.html",
        context={
            "count": len(uploaded),
            "files": uploaded,
            "failed": failed,
        },
    )
