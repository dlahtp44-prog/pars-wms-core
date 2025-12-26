from fastapi import APIRouter, Request
from ._common import templates
from app.db import get_conn

router = APIRouter()

@router.get("/dashboard")
def page(request: Request):
    # 간단 집계: 총 재고(수량 합)
    with get_conn() as conn:
        row = conn.execute("SELECT COALESCE(SUM(quantity),0) AS total FROM inventory").fetchone()
    return templates.TemplateResponse("dashboard.html", {"request": request, "total": int(row["total"])})
