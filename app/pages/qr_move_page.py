from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter(prefix="/qr", tags=["qr"])

@router.get("/move")
def page(request: Request):
    return templates.TemplateResponse("qr_move.html", {"request": request})
