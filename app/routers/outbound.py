
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/api/outbound")

@router.post("/excel")
async def outbound_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="엑셀(xlsx) 파일만 가능합니다")
    return {"result": "ok", "message": "출고 엑셀 처리 완료"}
