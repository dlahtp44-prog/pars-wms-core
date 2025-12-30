from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.core.downloads import pop_token

router = APIRouter(prefix="/download", tags=["download"])

@router.get("/{token}")
def download(token: str):
    item = pop_token(token)
    if not item:
        raise HTTPException(status_code=404, detail="다운로드 토큰이 없거나 만료되었습니다.")
    headers = {"Content-Disposition": f'attachment; filename="{item.filename}"'}
    return Response(content=item.data, media_type=item.content_type, headers=headers)
