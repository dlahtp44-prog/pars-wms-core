from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/m")
templates = Jinja2Templates(directory="app/templates")

@router.get("/qr")
def qr(request: Request):
    return templates.TemplateResponse("qr.html", {"request": request, "title": "QR 스캔"})
