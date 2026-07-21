from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.config import PHOTO_STORAGE
from app.services.storage import (
    list_people,
    list_files,
    get_all_files,
    get_display_name,
)
from app.web import templates

router = APIRouter()


@router.get("/gallery", response_class=HTMLResponse)
def gallery(request: Request):
    people = []
    total = 0
    for name in list_people():
        files = list(list_files(PHOTO_STORAGE / name))
        total += len(files)
        cover = None
        if files:
            cover = f"/thumbnail/{name}/{files[0].stem}.jpg"
        people.append(
            {
                "name": name,
                "display": get_display_name(name),
                "count": len(files),
                "cover": cover,
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="gallery.html",
        context={
            "people": people,
            "total": total,
        },
    )


@router.get("/gallery/all", response_class=HTMLResponse)
def gallery_all(request: Request):

    files = get_all_files()
    names = {person: get_display_name(person) for person, _ in files}

    return templates.TemplateResponse(
        request=request,
        name="gallery_all.html",
        context={
            "files": files,
            "names": names,
        },
    )


@router.get("/gallery/{person}", response_class=HTMLResponse)
def gallery_person(request: Request, person: str):

    if person not in list_people():
        raise HTTPException(
            status_code=404,
            detail="errors.album_not_found",
        )

    files = list(list_files(PHOTO_STORAGE / person))

    return templates.TemplateResponse(
        request=request,
        name="person.html",
        context={
            "person": person,
            "display": get_display_name(person),
            "files": files,
        },
    )
