
from fastapi import APIRouter
from app.db import get_db

router = APIRouter(prefix="/admin/location/summary")

@router.get("")
def summary():
    db = get_db()
    return db.execute("""
        SELECT l.location_code, l.is_active,
               COUNT(i.id) AS item_cnt,
               COALESCE(SUM(i.qty),0) AS total_qty
        FROM location_master l
        LEFT JOIN inventory i ON l.location_code = i.location_code
        GROUP BY l.location_code
    """).fetchall()
