from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/qr/로케이션", response_class=HTMLResponse)
def qr_location(request: Request):
    return templates.TemplateResponse("qr_location.html", {"request": request})


@router.get("/qr/이동", response_class=HTMLResponse)
def qr_move(request: Request):
    return templates.TemplateResponse("qr_move.html", {"request": request})


@router.get("/qr/출고", response_class=HTMLResponse)
def qr_outbound(request: Request):
    return templates.TemplateResponse("qr_outbound.html", {"request": request})

