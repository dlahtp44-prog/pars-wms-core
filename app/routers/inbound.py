from fastapi import APIRouter
from app.routers._models import InboundReq
from app import db

router = APIRouter(prefix="/api", tags=["inbound"])

@router.post("/inbound")
def api_inbound(req: InboundReq):
    # master upsert
    db.upsert_item(req.item_code, req.item_name, req.brand, req.spec)
    # inventory add
    db.add_inventory(
        item_code=req.item_code,
        location=req.location,
        lot=req.lot,
        quantity=req.quantity,
        item_name=req.item_name,
        brand=req.brand,
        spec=req.spec,
    )
    # history
    db.insert_history(
        action="INBOUND",
        item_code=req.item_code,
        item_name=req.item_name,
        lot=req.lot,
        quantity=req.quantity,
        location_from=None,
        location_to=req.location,
        remark=None,
    )
    return {"result": "ok"}
