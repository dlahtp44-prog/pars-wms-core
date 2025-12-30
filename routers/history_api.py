from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("")
def history(limit: int = Query(default=200)):
    limit = max(1, min(2000, limit))
    with get_db() as conn:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT ts, kind, location, src_location, item_code, item_name, lot, spec, brand, qty, note FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return {"rows": rows}
