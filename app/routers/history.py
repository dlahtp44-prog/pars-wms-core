from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api/이력", tags=["이력"])

@router.get("")
def 이력조회(limit: int = Query(200, ge=1, le=5000)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM 이력 ORDER BY id DESC LIMIT ?", (int(limit),))
    items = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(items), "items": items}
