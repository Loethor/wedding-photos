from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


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

        return RedirectResponse(
            "/login",
            status_code=303,
        )
