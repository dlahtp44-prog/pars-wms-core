from fastapi import APIRouter
from app.db import get_db

router = APIRouter(prefix="/api/이력", tags=["이력"])


@router.get("")
def 이력_조회():
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute("""
    SELECT id, 일시, 구분, 창고, 품번, LOT, 출발로케이션, 도착로케이션, 수량, 비고
    FROM 이력
    ORDER BY id DESC
    LIMIT 500
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
