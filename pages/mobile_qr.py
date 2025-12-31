
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/m/qr", response_class=HTMLResponse)
def mobile_qr(request: Request):
    return templates.TemplateResponse("mobile_qr.html", {"request": request})
