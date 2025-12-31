
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/m", response_class=HTMLResponse)
def mobile_home(request: Request):
    return templates.TemplateResponse("m/index.html", {"request": request})
