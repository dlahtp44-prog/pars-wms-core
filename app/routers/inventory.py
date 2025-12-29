
from fastapi import APIRouter
from app.db import get_db

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

@router.get("")
def inventory_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT location, item_code, lot, qty, updated_at
    FROM inventory
    ORDER BY updated_at DESC
    """)
    rows = cur.fetchall()
    return [
        {"location":r[0],"item_code":r[1],"lot":r[2],"qty":r[3],"updated_at":r[4]}
        for r in rows
    ]
