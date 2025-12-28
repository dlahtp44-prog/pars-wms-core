
from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from app.db import get_db

router = APIRouter(prefix="/calendar")

@router.post("/add")
def add_event(date: str = Form(...), content: str = Form(...)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO calendar (date, content) VALUES (?, ?)",
        (date, content)
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/calendar", status_code=302)
