from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter(prefix="/qr", tags=["qr"])

@router.get("/location")
def page(request: Request):
    return templates.TemplateResponse("qr_location.html", {"request": request})
