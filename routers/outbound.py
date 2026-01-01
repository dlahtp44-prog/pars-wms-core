
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/api/outbound")

@router.post("")
async def outbound_api(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(400, "엑셀(xlsx)만 가능")
    return {"result": "ok", "type": "outbound"}
