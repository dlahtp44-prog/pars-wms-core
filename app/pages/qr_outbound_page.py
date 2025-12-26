from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter(prefix="/qr", tags=["qr"])

@router.get("/outbound")
def page(request: Request):
    return templates.TemplateResponse("qr_outbound.html", {"request": request})
