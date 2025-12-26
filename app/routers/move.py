from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app import db

router = APIRouter(prefix="/api", tags=["move"])

# 프론트 키가 from_location/to_location 또는 location_from/location_to로 올 수 있어 둘 다 허용
class MoveReq(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    item_code: str
    item_name: Optional[str] = None
    lot: str
    quantity: int = Field(gt=0)

    from_location: Optional[str] = None
    to_location: Optional[str] = None

    location_from: Optional[str] = None
    location_to: Optional[str] = None

    remark: Optional[str] = None

    def normalized(self):
        frm = self.from_location or self.location_from
        to = self.to_location or self.location_to
        return frm, to

@router.post("/move")
async def api_move(req: Request):
    data = await req.json()
    m = MoveReq(**data)
    frm, to = m.normalized()
    if not frm or not to:
        raise HTTPException(status_code=422, detail="from_location/to_location(또는 location_from/location_to)가 필요합니다.")

    try:
        db.subtract_inventory_exact(m.item_code, frm, m.lot, m.quantity)
        db.add_inventory(m.item_code, to, m.lot, m.quantity, item_name=m.item_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.insert_history(
        action="MOVE",
        item_code=m.item_code,
        item_name=m.item_name,
        lot=m.lot,
        quantity=m.quantity,
        location_from=frm,
        location_to=to,
        remark=m.remark,
    )
    return {"result": "ok"}
