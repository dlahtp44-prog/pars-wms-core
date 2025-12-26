from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/캘린더", response_class=HTMLResponse)
def view(request: Request):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT 날짜, 제목, 내용 FROM 캘린더 ORDER BY 날짜 DESC, id DESC LIMIT 200")
    rows = cur.fetchall()
    conn.close()
    return templates.TemplateResponse("calendar.html", {"request": request, "rows": rows})

@router.post("/캘린더", response_class=HTMLResponse)
def add(request: Request, 날짜: str = Form(...), 제목: str = Form(...), 내용: str = Form(...)):
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO 캘린더(날짜, 제목, 내용) VALUES(?,?,?)", (날짜, 제목.strip(), 내용.strip()))
    conn.commit(); conn.close()
    return view(request)
