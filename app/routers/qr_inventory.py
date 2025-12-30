from fastapi import APIRouter

router = APIRouter(prefix="/api/qr", tags=["QR"])

@router.get("/inventory/{location}")
def qr_inventory(location: str):
    """
    QR 로케이션 스캔 → 재고 목록 반환
    (현재는 테스트 데이터)
    """
    return {
        "location": location,
        "items": [
            {
                "item_code": "TEST001",
                "item_name": "샘플상품",
                "lot": "LOT001",
                "spec": "100x100",
                "qty": 10
            }
        ]
    }
