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

    sql = f"""
    SELECT location, item_code, item_name, lot, spec, brand, SUM(delta_qty) AS qty
    FROM (
        SELECT location, item_code, item_name, lot, spec, brand, qty AS delta_qty
        FROM inbound
        UNION ALL
        SELECT location, item_code, item_name, lot, spec, brand, -qty AS delta_qty
        FROM outbound
        UNION ALL
        SELECT src_location AS location, item_code, item_name, lot, spec, brand, -qty AS delta_qty
        FROM moves
        UNION ALL
        SELECT dst_location AS location, item_code, item_name, lot, spec, brand, qty AS delta_qty
        FROM moves
    )
    {where_sql}
    GROUP BY location, item_code, item_name, lot, spec, brand
    HAVING qty != 0
    ORDER BY location, item_code, lot
    """
    with get_db() as conn:
        cur = conn.cursor()
        rows = cur.execute(sql, params).fetchall()
    return {"rows": rows}
