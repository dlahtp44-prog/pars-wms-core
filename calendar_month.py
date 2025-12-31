from fastapi import APIRouter, Query, Request
from fastapi.templating import Jinja2Templates
from datetime import date
import calendar

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/page/calendar/month")
def calendar_month(
    request: Request,
    year: int = Query(default=date.today().year),
    month: int = Query(default=date.today().month),
):
    cal = calendar.Calendar()
    weeks = cal.monthdayscalendar(year, month)

    return templates.TemplateResponse(
        "calendar_month.html",
        {
            "request": request,
            "year": year,
            "month": month,
            "weeks": weeks,
            "prev_year": year - 1 if month == 1 else year,
            "prev_month": 12 if month == 1 else month - 1,
            "next_year": year + 1 if month == 12 else year,
            "next_month": 1 if month == 12 else month + 1,
        }
    )
