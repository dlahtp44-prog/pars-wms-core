from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api/재고", tags=["재고"])


@router.get("")
def 재고_전체():
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute("""
    SELECT 창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고
    FROM 재고
    ORDER BY 창고, 로케이션, 품번, LOT
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/로케이션")
def 재고_로케이션(
    창고: str = Query(...),
    로케이션: str = Query(...)
):
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute("""
    SELECT 창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고
    FROM 재고
    WHERE 창고=? AND 로케이션=?
    ORDER BY 품번, LOT
    """, (창고.strip(), 로케이션.strip())).fetchall()
    conn.close()
    return [dict(r) for r in rows]
