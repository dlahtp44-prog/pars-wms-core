from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "title": "PARS WMS"})
