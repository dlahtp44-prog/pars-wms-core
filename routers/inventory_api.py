from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

@router.get("")
def inventory(location: str | None = Query(default=None), item_code: str | None = Query(default=None)):
    where = []
    params = []
    if location:
        where.append("location LIKE ?")
        params.append(f"%{location}%")
    if item_code:
        where.append("item_code LIKE ?")
        params.append(f"%{item_code}%")
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    with get_db() as conn:
        cur = conn.cursor()
        rows = cur.execute(
            f"""SELECT location,item_code,item_name,lot,spec,brand,qty,updated_at,note
                 FROM inventory {where_sql}
                 ORDER BY location, item_code, lot""",
            params,
        ).fetchall()
    return {"rows": rows}
