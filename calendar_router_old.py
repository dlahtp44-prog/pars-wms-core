"""(LEGACY)

이 파일은 과거 버전에서 사용하던 달력 페이지 라우터입니다.

⚠️ 주의: 표준라이브러리 `calendar` 모듈과 파일명이 충돌하면 FastAPI 구동 시
예기치 못한 ImportError(순환 import)가 발생할 수 있어 파일명을 변경했습니다.

현재 PARS WMS v2에서는 `app/main.py` 의 `/page/calendar/month` 라우트를 사용합니다.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
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
    return templates.TemplateResponse(
        "calendar.html",
        {"request": request, "rows": rows},
    )
