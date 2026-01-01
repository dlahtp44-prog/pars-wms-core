from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from datetime import date

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/page/calendar/month")
def calendar_month(
    request: Request,
    year: int = Query(default=date.today().year),
    month: int = Query(default=date.today().month),
):
    return templates.TemplateResponse(
        "calendar_month.html",
        {
            "request": request,
            "year": year,
            "month": month,
        }
    )