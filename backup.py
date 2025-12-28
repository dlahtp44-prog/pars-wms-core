
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.auth import require_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin/backup", response_class=HTMLResponse)
def backup_page(request: Request):
    r = require_admin(request)
    if r:
        return r
    return templates.TemplateResponse("backup.html", {"request": request})
