from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
@router.get("/재고", response_class=HTMLResponse)
def page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})
