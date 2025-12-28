
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/qr/이동", response_class=HTMLResponse)
def qr_move_page(request: Request):
    return templates.TemplateResponse("qr_move.html", {"request": request})
