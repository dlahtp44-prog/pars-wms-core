from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/m")

@router.get("")
def mobile_home(request: Request):
    return templates.TemplateResponse("mobile_home.html", {"request": request})
