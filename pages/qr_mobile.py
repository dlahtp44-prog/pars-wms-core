from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR

router = APIRouter(prefix="/m/qr", tags=["mobile-qr"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("")
def qr_home(request: Request):
    return templates.TemplateResponse("qr.html", {"request": request, "title":"QR 스캔"})
