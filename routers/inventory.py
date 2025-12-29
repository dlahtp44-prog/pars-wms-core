
from fastapi import APIRouter
from app.db import get_db

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

@router.get("")
def inventory_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT 
        location,
        item_code,
        lot,
        spec,
        brand,
        qty,
        updated_at,
        memo
    FROM inventory
    ORDER BY updated_at DESC
    """)
    rows = cur.fetchall()
    return [
        {
            "location": r[0],
            "item_code": r[1],
            "lot": r[2],
            "spec": r[3],
            "brand": r[4],
            "qty": r[5],
            "updated_at": r[6],
            "memo": r[7],
        }
        for r in rows
    ]
