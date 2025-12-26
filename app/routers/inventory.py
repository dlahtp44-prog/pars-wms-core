from fastapi import APIRouter
from app.db import get_db

router = APIRouter(prefix="/api/재고", tags=["재고"])

@router.get("")
def 재고조회():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM 재고 ORDER BY updated_at DESC, id DESC")
    items = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(items), "items": items}
