from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/page/outbound")

@router.get("")
def page(request: Request):
    return templates.TemplateResponse("outbound.html", {"request": request, "title": "출고등록"})
