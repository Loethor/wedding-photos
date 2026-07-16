from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi import HTTPException

from starlette.middleware.sessions import SessionMiddleware

from app.config import SECRET_KEY, SESSION_MAX_AGE
from app.middleware.authentication import AuthenticationMiddleware
from app.routes import auth, files, gallery, upload
from app.web import templates

app = FastAPI()
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(gallery.router)
app.include_router(files.router)

app.add_middleware(
    AuthenticationMiddleware,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=SESSION_MAX_AGE,
    https_only=True,
    same_site="lax",
)


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
