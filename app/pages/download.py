from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.downloads import get_path

router = APIRouter(prefix="/download", tags=["download"])

@router.get("/{token}")
def download(token: str):
    path = get_path(token)
    if not path:
        raise HTTPException(status_code=404, detail="다운로드 파일이 만료되었거나 없습니다.")
    return FileResponse(
        path,
        filename=path.split("/")[-1],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
