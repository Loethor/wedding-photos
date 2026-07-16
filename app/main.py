from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.services.storage import (
    list_people,
    list_files,
    get_all_files,
    IMAGE_EXTENSIONS,
)

from app.services.storage import save_file


from app.services.thumbnails import create_thumbnail

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse

from app.config import PHOTO_STORAGE, SECRET_KEY, WEDDING_PASSWORD


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        public_paths = {
            "/login",
            "/favicon.ico",
        }

        if request.url.path in public_paths:
            return await call_next(request)

        if request.session.get("authenticated"):
            return await call_next(request)

        return RedirectResponse("/login", status_code=303)


app = FastAPI()

app.add_middleware(
    AuthenticationMiddleware,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=60 * 60 * 24 * 30,
)

templates = Jinja2Templates(directory="app/templates")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": False},
    )


@app.post("/login")
def login(
    request: Request,
    password: str = Form(...),
):
    if password != WEDDING_PASSWORD:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": True},
        )

    request.session["authenticated"] = True

    return RedirectResponse("/", status_code=303)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/photo/{person}/{filename}")
def serve_photo(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    if not file.exists():
        return {"error": "File not found"}

    return FileResponse(file)


@app.get("/video/{person}/{filename}")
def serve_video(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    if not file.exists():
        return {"error": "Video not found"}

    return FileResponse(file, media_type="video/mp4")


@app.get("/download/{person}/{filename}")
def download_file(person: str, filename: str):

    file = PHOTO_STORAGE / person / filename

    if not file.exists():
        return {"error": "File not found"}

    return FileResponse(file, filename=file.name)


@app.get("/thumbnail/{person}/{filename}")
def serve_thumbnail(person: str, filename: str):

    file = PHOTO_STORAGE / ".thumbnails" / person / filename

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

    for file in files:
        content = await file.read()

        saved = save_file(username, file.filename, content)

        uploaded.append(str(saved))

    return templates.TemplateResponse(
        request=request, name="upload_success.html", context={"count": len(uploaded)}
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


def is_image(file: Path) -> bool:
    return file.suffix.lower() in IMAGE_EXTENSIONS


def is_video(file: Path) -> bool:
    return file.suffix.lower() in {
        ".mp4",
        ".mov",
    }


@app.get("/gallery/{person}", response_class=HTMLResponse)
def gallery_person(request: Request, person: str):
    folder = PHOTO_STORAGE / person

    files = []

    for file in list_files(folder):
        if is_image(file):
            create_thumbnail(person, file)

        files.append(file)

    return templates.TemplateResponse(
        request=request, name="person.html", context={"person": person, "files": files}
    )
