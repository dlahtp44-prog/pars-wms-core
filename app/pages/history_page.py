from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/page/history")

@router.get("")
def page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request, "title": "이력조회"})
