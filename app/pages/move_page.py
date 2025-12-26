from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter()

@router.get("/move")
def page(request: Request):
    return templates.TemplateResponse("move.html", {"request": request})
