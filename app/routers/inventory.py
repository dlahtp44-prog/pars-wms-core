from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api/재고", tags=["재고"])


@router.get("")
def 재고조회(
    창고: str | None = Query(None),
    로케이션: str | None = Query(None),
    품번: str | None = Query(None),
    LOT: str | None = Query(None),
):
    conn = get_db()
    cur = conn.cursor()

    where = []
    params = []

    if 창고:
        where.append("창고=?")
        params.append(창고.strip())
    if 로케이션:
        where.append("로케이션=?")
        params.append(로케이션.strip())
    if 품번:
        where.append("품번=?")
        params.append(품번.strip())
    if LOT:
        where.append("LOT=?")
        params.append(LOT.strip())

    sql = "SELECT 창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고, updated_at FROM 재고"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY 창고, 로케이션, 품번, LOT"

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "items": [dict(r) for r in rows]
    }
