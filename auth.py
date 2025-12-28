
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.db import get_db

router = APIRouter()

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    conn.close()

    if not row:
        return RedirectResponse("/login?error=1", status_code=302)

    request.session["user"] = username
    request.session["role"] = row[0]
    return RedirectResponse("/", status_code=302)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
