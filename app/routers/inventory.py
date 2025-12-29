
from fastapi import APIRouter
from app.db import get_db

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

@router.get("")
def inventory_list(location: str = "", item_code: str = ""):
    conn = get_db()
    cur = conn.cursor()

    sql = "SELECT location, item_code, lot, qty, updated_at FROM inventory WHERE 1=1"
    params = []

    if location:
        sql += " AND location LIKE ?"
        params.append(f"%{location}%")

    if item_code:
        sql += " AND item_code LIKE ?"
        params.append(f"%{item_code}%")

    cur.execute(sql, params)
    rows = cur.fetchall()

    return [
        {
            "location": r[0],
            "item_code": r[1],
            "lot": r[2],
            "qty": r[3],
            "updated_at": r[4]
        }
        for r in rows
    ]
