from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.config import SECRET_KEY, SESSION_MAX_AGE, SECURE_COOKIES
from app.middleware.authentication import AuthenticationMiddleware
from app.routes import auth, files, gallery, upload
from app.services.i18n import Translator, resolve_locale
from app.web import templates

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI()
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(gallery.router)
app.include_router(files.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    AuthenticationMiddleware,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=SESSION_MAX_AGE,
    https_only=SECURE_COOKIES,
    same_site="lax",
)


def render_error(request: Request, status_code: int, detail: str) -> HTMLResponse:
    locale = resolve_locale(request.headers.get("accept-language"))
    message = Translator(locale)(str(detail))

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "message": message,
        },
        status_code=status_code,
    )


# Registrado sobre la HTTPException de Starlette (clase padre) para cubrir también
# los 404/405 que lanza el propio framework, no solo las que lanzamos nosotros.
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return render_error(request, exc.status_code, exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return render_error(request, 400, "errors.bad_request")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})
