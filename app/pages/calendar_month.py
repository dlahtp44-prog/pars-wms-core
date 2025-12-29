from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from datetime import date
import calendar
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

    # year/month 없으면 오늘 기준으로 리다이렉트
    if year is None or month is None:
        return RedirectResponse(
            url=f"/page/calendar/month?year={today.year}&month={today.month}"
        )

    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    weeks = cal.monthdayscalendar(year, month)
    # weeks 예시:
    # [[0, 0, 1, 2, 3, 4, 5],
    #  [6, 7, 8, 9, 10, 11, 12], ...]

    return templates.TemplateResponse(
        "calendar_month.html",
        {
            "request": request,
            "year": year,
            "month": month,
            "weeks": weeks,
            "prev_year": year - 1 if month == 1 else y_
