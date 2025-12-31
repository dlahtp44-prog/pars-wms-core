
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/m/qr", response_class=HTMLResponse)
def mobile_qr(request: Request):
    return templates.TemplateResponse("m/qr.html", {"request": request})
