from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter()

@router.get("/inbound")
def page(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})
