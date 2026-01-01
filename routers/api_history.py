from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api/이력", tags=["이력"])

@router.get("")
def 이력조회(limit: int = Query(default=200, ge=1, le=2000), 구분: str | None = None):
    conn = get_db(); cur = conn.cursor()
    if 구분:
        cur.execute(
            """SELECT id, 구분, 창고, 품번, 품명, LOT, 규격, 출발로케이션, 도착로케이션, 수량, 비고, created_at
                 FROM 이력 WHERE 구분=? ORDER BY id DESC LIMIT ?""",
            (구분, limit)
        )
    else:
        cur.execute(
            """SELECT id, 구분, 창고, 품번, 품명, LOT, 규격, 출발로케이션, 도착로케이션, 수량, 비고, created_at
                 FROM 이력 ORDER BY id DESC LIMIT ?""",
            (limit,)
        )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "items": rows}
