
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/calendar", response_class=HTMLResponse)
def calendar_page(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT date, content FROM calendar ORDER BY date")
    rows = cur.fetchall()
    conn.close()
    return templates.TemplateResponse("calendar.html", {"request": request, "rows": rows})

@router.post("/calendar")
def calendar_save(date: str = Form(...), content: str = Form(...)):
    date = (date or "").strip()
    content = (content or "").strip()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO calendar(date, content) VALUES(?, ?) ON CONFLICT(date) DO UPDATE SET content=excluded.content", (date, content))
    conn.commit()
    conn.close()
    return RedirectResponse("/calendar", status_code=303)
