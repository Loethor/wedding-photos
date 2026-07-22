from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import WEDDING_PASSWORD
from app.services.rate_limit import RateLimiter

from app.logger import logger
from app.web import templates

router = APIRouter()


login_limiter = RateLimiter(
    max_attempts=5,
    window_seconds=60,
)


@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": False},
    )


@router.post("/login")
def login(
    request: Request,
    password: str = Form(...),
):

    ip = request.client.host if request.client else "unknown"

    if not login_limiter.allow(ip):
        logger.warning(
            "Login blocked: %s",
            ip,
        )

        raise HTTPException(
            status_code=429,
            detail="errors.too_many_attempts",
        )

    if password != WEDDING_PASSWORD:
        logger.warning(
            "Invalid login: %s",
            ip,
        )

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": True},
            status_code=401,
        )

    request.session["authenticated"] = True

    return RedirectResponse(
        "/",
        status_code=303,
    )
