from fastapi import APIRouter, HTTPException
from app.routers._models import OutboundReq
from app import db

router = APIRouter(prefix="/api", tags=["outbound"])

@router.post("/outbound")
def api_outbound(req: OutboundReq):
    try:
        taken = db.subtract_inventory_any_location(
            item_code=req.item_code,
            lot=req.lot,
            quantity=req.quantity,
            prefer_location=req.location,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # history: 여러 로케이션에서 차감될 수 있으니 분할 기록
    for loc, qty in taken:
        db.insert_history(
            action="OUTBOUND",
            item_code=req.item_code,
            item_name=req.item_name,
            lot=req.lot,
            quantity=qty,
            location_from=loc,
            location_to=None,
            remark=req.remark,
        )
    return {"result": "ok", "taken": taken}
