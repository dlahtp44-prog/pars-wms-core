from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR
from fastapi.responses import RedirectResponse
from datetime import datetime
from zoneinfo import ZoneInfo
import calendar as _cal

from app.db import get_db, now_kst_iso

router = APIRouter(prefix="/page/calendar", tags=["page-calendar"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def _month_grid(year: int, month: int):
    cal = _cal.Calendar(firstweekday=6)  # Sunday
    return cal.monthdatescalendar(year, month)

@router.get("/month")
def calendar_month(request: Request, year: int, month: int, ymd: str = ""):
    grid = _month_grid(year, month)
    # memos count per day in month
    conn=get_db()
    cur=conn.cursor()
    start=f"{year:04d}-{month:02d}-01"
    # end month
    last_day=_cal.monthrange(year, month)[1]
    end=f"{year:04d}-{month:02d}-{last_day:02d}"
    cur.execute("SELECT ymd, COUNT(*) as c FROM calendar_memo WHERE ymd BETWEEN ? AND ? GROUP BY ymd", (start, end))
    counts={row["ymd"]: row["c"] for row in cur.fetchall()}

    selected = ymd or datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
    cur.execute("SELECT id,ymd,author,memo,created_at FROM calendar_memo WHERE ymd=? ORDER BY id DESC", (selected,))
    memos=cur.fetchall()
    conn.close()

    prev_y, prev_m = (year-1, 12) if month==1 else (year, month-1)
    next_y, next_m = (year+1, 1) if month==12 else (year, month+1)

    return templates.TemplateResponse("calendar_month.html", {
        "request": request,
        "title": "달력(월간)",
        "year": year,
        "month": month,
        "grid": grid,
        "counts": counts,
        "selected": selected,
        "memos": memos,
        "prev_y": prev_y, "prev_m": prev_m,
        "next_y": next_y, "next_m": next_m,
    })

@router.post("/memo/add")
def add_memo(year: int = Form(...), month: int = Form(...), ymd: str = Form(...), author: str = Form(""), memo: str = Form(...)):
    memo = (memo or "").strip()
    if not memo:
        return RedirectResponse(url=f"/page/calendar/month?year={year}&month={month}", status_code=303)

    conn=get_db()
    cur=conn.cursor()
    cur.execute(
        "INSERT INTO calendar_memo(ymd,author,memo,created_at) VALUES (?,?,?,?)",
        (ymd, author.strip(), memo, now_kst_iso()),
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/page/calendar/month?year={year}&month={month}&ymd={ymd}", status_code=303)
