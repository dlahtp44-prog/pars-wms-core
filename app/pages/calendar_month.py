from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from datetime import date
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/page/calendar/month")
def calendar_month(
    request: Request,
    year: int | None = None,
    month: int | None = None,
):
    today = date.today()

    # ✅ year/month 없이 접근하면 오늘 기준으로 리다이렉트
    if year is None or month is None:
        return RedirectResponse(
            url=f"/page/calendar/month?year={today.year}&month={today.month}"
        )

    return templates.TemplateResponse(
        "calendar_month.html",
        {
            "request": request,
            "year": year,
            "month": month,
            "prev_year": year - 1 if month == 1 else year,
            "prev_month": 12 if month == 1 else month - 1,
            "next_year": year + 1 if month == 12 else year,
            "next_month": 1 if month == 12 else month + 1,
        },
    )
