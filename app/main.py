from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException


from app.services.storage import (
    list_people,
    list_files,
    get_all_files,
)

from app.services.storage import save_file


from app.services.thumbnails import create_thumbnail

from starlette.middleware.sessions import SessionMiddleware
from app.services.security import safe_path
from app.config import PHOTO_STORAGE, SECRET_KEY, MAX_UPLOAD_SIZE

from app.middleware.authentication import AuthenticationMiddleware


import logging

from app.routes import auth, files

logger = logging.getLogger("wedding-photos")
logging.basicConfig(level=logging.INFO)


app = FastAPI()
app.include_router(auth.router)
app.include_router(files.router)

app.add_middleware(
    AuthenticationMiddleware,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=60 * 60 * 24 * 30,
    https_only=True,
    same_site="lax",
)

templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "message": exc.detail,
        },
        status_code=exc.status_code,
    )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/thumbnail/{person}/{filename}")
def serve_thumbnail(person: str, filename: str):

    file = PHOTO_STORAGE / ".thumbnails" / person / filename

    if not safe_path(file):
        return {"error": "Invalid path"}

    if not file.exists():
        return {"error": "Thumbnail not found"}

    return FileResponse(file)


@app.post("/upload")
async def upload(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    files: list[UploadFile] = File(...),
):
    username = f"{first_name}_{last_name}"
    uploaded = []

    logger.info(
        "Upload started: user=%s files=%d",
        username,
        len(files),
    )

    for file in files:
        logger.info(
            "Processing file: %s",
            file.filename,
        )

        try:
            saved, size = save_file(
                username,
                file.filename,
                file.file,
                MAX_UPLOAD_SIZE,
            )

        except ValueError:
            logger.warning(
                "Upload rejected: %s too large",
                file.filename,
            )

            raise HTTPException(
                status_code=413,
                detail=f"{file.filename} is too large",
            )

        logger.info(
            "Saved %s (%.2f MB)",
            saved,
            size / 1024 / 1024,
        )

        create_thumbnail(
            username,
            saved,
        )

        uploaded.append(saved.name)

    logger.info(
        "Upload completed: user=%s files=%d",
        username,
        len(uploaded),
    )

    return templates.TemplateResponse(
        request=request,
        name="upload_success.html",
        context={
            "count": len(uploaded),
            "files": uploaded,
        },
    )


@app.get("/gallery", response_class=HTMLResponse)
def gallery(request: Request):
    return templates.TemplateResponse(
        request=request, name="gallery.html", context={"people": list_people()}
    )


@app.get("/gallery/all", response_class=HTMLResponse)
def gallery_all(request: Request):
    files = get_all_files()

    return templates.TemplateResponse(
        request=request, name="gallery_all.html", context={"files": files}
    )


@app.get("/gallery/{person}", response_class=HTMLResponse)
def gallery_person(request: Request, person: str):
    folder = PHOTO_STORAGE / person

    files = []

    for file in list_files(folder):
        files.append(file)

    return templates.TemplateResponse(
        request=request, name="person.html", context={"person": person, "files": files}
    )
