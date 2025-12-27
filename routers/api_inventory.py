from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api/재고", tags=["재고"])

@router.get("")
def 재고조회(
    창고: str | None = Query(default=None),
    로케이션: str | None = Query(default=None),
    품번: str | None = Query(default=None),
    LOT: str | None = Query(default=None),
):
    conn = get_db(); cur = conn.cursor()
    sql = "SELECT 창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고, updated_at FROM 재고 WHERE 1=1"
    params = []
    if 창고:
        sql += " AND 창고=?"; params.append(창고)
    if 로케이션:
        sql += " AND 로케이션=?"; params.append(로케이션)
    if 품번:
        sql += " AND 품번=?"; params.append(품번)
    if LOT:
        sql += " AND LOT=?"; params.append(LOT)
    sql += " ORDER BY 창고, 로케이션, 품번, LOT"
    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "items": rows}
