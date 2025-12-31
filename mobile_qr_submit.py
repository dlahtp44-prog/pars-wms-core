from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.post("/m/qr/submit")
def qr_submit(location: str = Form(...)):
    """
    모바일 QR 스캔 결과를 받아
    서버에서 재고 조회 페이지로 redirect
    (iOS Safari 차단 불가 방식)
    """
    return RedirectResponse(
        url=f"/m/qr/inventory?location={location}",
        status_code=302
    )
