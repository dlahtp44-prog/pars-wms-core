from fastapi import APIRouter, Form, HTTPException, Query
from app.db import get_db, now_ts

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

@router.post("/memo")
def add_memo(
    ymd: str = Form(...),
    memo: str = Form(...),
    author: str = Form(""),
):
    ymd = ymd.strip()
    memo = memo.strip()
    if not ymd or not memo:
        raise HTTPException(status_code=400, detail="날짜와 메모는 필수입니다.")
    ts = now_ts()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO calendar_memo(ymd,author,memo,created_at) VALUES(?,?,?,?)",
            (ymd, author, memo, ts),
        )
    return {"ok": True}

@router.get("/memo")
def list_memo(month: str = Query(...)):  # month = YYYY-MM
    month = month.strip()
    if len(month) != 7:
        raise HTTPException(status_code=400, detail="month는 YYYY-MM 형식이어야 합니다.")
    with get_db() as conn:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT ymd, author, memo FROM calendar_memo WHERE ymd LIKE ? ORDER BY ymd, id",
            (month + "-%",),
        ).fetchall()
    return {"rows": rows}
