from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/page/move")

@router.get("")
def page(request: Request):
    return templates.TemplateResponse("move.html", {"request": request, "title": "이동등록"})
