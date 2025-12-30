
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/m/qr", tags=["Mobile QR"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def mobile_qr(request: Request):
    return templates.TemplateResponse("mobile/qr_scan.html", {"request": request})
