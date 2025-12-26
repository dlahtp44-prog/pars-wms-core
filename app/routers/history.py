from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api/이력", tags=["이력"])


@router.get("")
def 이력조회(
    limit: int = Query(200, ge=1, le=2000),
    구분: str | None = Query(None),
    창고: str | None = Query(None),
    품번: str | None = Query(None),
    LOT: str | None = Query(None),
):
    conn = get_db()
    cur = conn.cursor()

    where = []
    params = []

    if 구분:
        where.append("구분=?")
        params.append(구분.strip())
    if 창고:
        where.append("창고=?")
        params.append(창고.strip())
    if 품번:
        where.append("품번=?")
        params.append(품번.strip())
    if LOT:
        where.append("LOT=?")
        params.append(LOT.strip())

    sql = """
    SELECT 일시, 구분, 창고, 품번, LOT, 출발로케이션, 도착로케이션, 수량, 비고
    FROM 이력
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(int(limit))

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "items": [dict(r) for r in rows]
    }
