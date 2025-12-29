from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db
import calendar, datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/page/calendar/month", response_class=HTMLResponse)
def calendar_month(request: Request, year: int, month: int):
    cal = calendar.Calendar(6)
    today = datetime.date.today()
    db = get_db()
    days = []
    for d in cal.itermonthdates(year, month):
        rows = db.execute(
            "SELECT memo FROM calendar_memo WHERE date=? ORDER BY id",
            (d.isoformat(),)
        ).fetchall()
        days.append({
            "date": d,
            "date_iso": d.isoformat(),
            "memos": [dict(r) for r in rows],
            "is_today": d == today,
            "is_weekend": d.weekday() >= 5
        })
    pm, py = (12, year-1) if month == 1 else (month-1, year)
    nm, ny = (1, year+1) if month == 12 else (month+1, year)
    return templates.TemplateResponse("calendar_month.html", {
        "request": request,
        "days": days,
        "year": year,
        "month": month,
        "prev_year": py,
        "prev_month": pm,
        "next_year": ny,
        "next_month": nm
    })
