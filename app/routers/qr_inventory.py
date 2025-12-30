from fastapi import APIRouter
from app.db import search_inventory

router = APIRouter(prefix="/api/qr", tags=["QR"])

@router.get("/inventory/{location}")
def qr_inventory(location: str):
    rows = search_inventory(location=location)

    return {
        "location": location,
        "items": [
            {
                "item_code": r.item_code,
                "item_name": r.item_name,
                "lot": r.lot,
                "spec": r.spec,
                "qty": r.qty,
            }
            for r in rows
        ]
    }
