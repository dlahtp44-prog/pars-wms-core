from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/page/inventory")

@router.get("")
def page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request, "title": "재고 조회"})
