
from fastapi import APIRouter
from app.db import get_db
router = APIRouter(prefix="/api/재고")

@router.get("")
def inventory():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM 재고")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count":len(rows),"items":rows}
