from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db
import calendar
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/page/calendar/month", response_class=HTMLResponse)
def calendar_month(request: Request, year: int | None = None, month: int | None = None):
    today = datetime.date.today()
    if year is None or month is None:
        # 4) 오늘 기준 월 자동 이동
        return RedirectResponse(url=f"/page/calendar/month?year={today.year}&month={today.month}", status_code=302)

    # month 유효성 보정
    if month < 1: month = 1
    if month > 12: month = 12

    cal = calendar.Calendar(6)  # 일요일 시작
    db = get_db()

    days = []
    for d in cal.itermonthdates(year, month):
        rows = db.execute(
            "SELECT memo FROM calendar_memo WHERE date=? ORDER BY id ASC",
            (d.isoformat(),)
        ).fetchall()

        days.append({
            "date": d,
            "date_iso": d.isoformat(),
            "memos": [dict(r) for r in rows],
            "is_today": d == today,
            "is_weekend": d.weekday() >= 5,
        })

    db.close()

    pm, py = (12, year - 1) if month == 1 else (month - 1, year)
    nm, ny = (1, year + 1) if month == 12 else (month + 1, year)

    return templates.TemplateResponse(
        "calendar_month.html",
        {
            "request": request,
            "days": days,
            "year": year,
            "month": month,
            "prev_year": py,
            "prev_month": pm,
            "next_year": ny,
            "next_month": nm,
            "today_iso": today.isoformat(),
            "today_year": today.year,
            "today_month": today.month,
        },
    )
