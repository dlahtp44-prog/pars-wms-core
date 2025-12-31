from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR

router = APIRouter(prefix="/page/admin", tags=["page-admin"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("")
def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request, "title":"관리자"})
