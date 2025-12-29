
from fastapi import APIRouter
from app.db import get_db

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("")
def history_list():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT created_at, type, item_code, lot, qty, memo
    FROM history
    ORDER BY created_at DESC
    """)

    rows = cur.fetchall()
    return [
        {
            "time": r[0],
            "type": r[1],
            "item": f"{r[2]} / {r[3]}",
            "qty": r[4],
            "memo": r[5]
        }
        for r in rows
    ]
