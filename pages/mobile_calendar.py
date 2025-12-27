
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/m/calendar", response_class=HTMLResponse)
def mobile_calendar(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT date, content FROM calendar ORDER BY date")
    rows = cur.fetchall()
    conn.close()
    return templates.TemplateResponse("mobile_calendar.html", {"request": request, "rows": rows})
