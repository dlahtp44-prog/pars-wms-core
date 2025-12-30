from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date, datetime
import calendar as _cal

from app.db import get_db

router = APIRouter(prefix="/page/calendar")
templates = Jinja2Templates(directory="app/templates")

@router.get("/month")
def calendar_month(
    request: Request,
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
):
    today = date.today()
    y = year or today.year
    m = month or today.month

    # if missing params, redirect to canonical URL to avoid 422 and keep browser shareable
    if year is None or month is None:
        return RedirectResponse(url=f"/page/calendar/month?year={y}&month={m}", status_code=307)

    # build weeks matrix (list of weeks, each week list of 7 day numbers or 0)
    cal = _cal.Calendar(firstweekday=6)  # Sunday=6 so grid starts with Sun
    weeks = cal.monthdayscalendar(y, m)

    # fetch memos for this month
    ym_prefix = f"{y:04d}-{m:02d}-"
    with get_db() as conn:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT ymd, author, memo FROM calendar_memo WHERE ymd LIKE ? ORDER BY ymd, id",
            (ym_prefix + "%",),
        ).fetchall()

    memos_by_day: dict[int, list[dict]] = {}
    for r in rows:
        try:
            d = int(r["ymd"].split("-")[2])
        except Exception:
            continue
        memos_by_day.setdefault(d, []).append({"author": r.get("author",""), "memo": r.get("memo","")})

    prev_y, prev_m = (y - 1, 12) if m == 1 else (y, m - 1)
    next_y, next_m = (y + 1, 1) if m == 12 else (y, m + 1)

    return templates.TemplateResponse(
        "calendar_month.html",
        {
            "request": request,
            "title": "달력(월간)",
            "year": y,
            "month": m,
            "weeks": weeks,
            "memos_by_day": memos_by_day,
            "prev_year": prev_y,
            "prev_month": prev_m,
            "next_year": next_y,
            "next_month": next_m,
            "today_ymd": today.strftime("%Y-%m-%d"),
        },
    )
