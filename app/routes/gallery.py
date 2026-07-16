from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import PHOTO_STORAGE
from app.services.storage import (
    list_people,
    list_files,
    get_all_files,
)
from app.web import templates

router = APIRouter()


@router.get("/gallery", response_class=HTMLResponse)
def gallery(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="gallery.html",
        context={
            "people": list_people(),
        },
    )


@router.get("/gallery/all", response_class=HTMLResponse)
def gallery_all(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="gallery_all.html",
        context={
            "files": get_all_files(),
        },
    )


@router.get("/gallery/{person}", response_class=HTMLResponse)
def gallery_person(request: Request, person: str):

    files = list(list_files(PHOTO_STORAGE / person))

    return templates.TemplateResponse(
        request=request,
        name="person.html",
        context={
            "person": person,
            "files": files,
        },
    )
