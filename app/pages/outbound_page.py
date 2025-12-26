from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter()

@router.get("/outbound")
def page(request: Request):
    return templates.TemplateResponse("outbound.html", {"request": request})
