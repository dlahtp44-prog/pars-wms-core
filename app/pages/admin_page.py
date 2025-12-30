from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/page/admin")

@router.get("")
def page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request, "title": "관리자"})
