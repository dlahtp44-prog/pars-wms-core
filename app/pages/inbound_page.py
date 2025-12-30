from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/page/inbound")

@router.get("")
def page(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request, "title": "입고등록"})
