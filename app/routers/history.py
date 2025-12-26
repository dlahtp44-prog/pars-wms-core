from fastapi import APIRouter
from app.db import get_conn

router = APIRouter(prefix="/api", tags=["history"])

@router.get("/history")
def api_history():
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT action, item_code, item_name, location_from, location_to, lot, quantity, created_at
            FROM history
            ORDER BY id DESC
            LIMIT 300"""
        ).fetchall()
    return [dict(r) for r in rows]
