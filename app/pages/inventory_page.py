from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter()

@router.get("/inventory")
def page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})
