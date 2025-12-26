from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter()

@router.get("/history")
def page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})
