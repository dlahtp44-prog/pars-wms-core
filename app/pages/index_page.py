from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter()

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
