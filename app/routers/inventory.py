from fastapi import APIRouter
from app.db import get_conn

router = APIRouter(prefix="/api", tags=["inventory"])

@router.get("/inventory")
def api_inventory():
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT item_code, item_name, brand, spec, location, lot, quantity
            FROM inventory
            WHERE quantity > 0
            ORDER BY location, item_code"""
        ).fetchall()
    return [dict(r) for r in rows]

@router.get("/inventory/by-location/{location}")
def api_inventory_by_location(location: str):
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT item_code, item_name, brand, spec, lot, quantity
            FROM inventory
            WHERE location=? AND quantity>0
            ORDER BY item_code, lot""",
            (location,)
        ).fetchall()
    return [dict(r) for r in rows]
