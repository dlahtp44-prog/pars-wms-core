
from fastapi import APIRouter

router = APIRouter(prefix="/api/qr")

@router.get("/inventory/{location}")
def qr_inventory(location: str):
    return {
        "location": location,
        "items": [
            {"품번": "TEST001", "품명": "샘플", "LOT": "L001", "규격": "100x100", "수량": 10}
        ]
    }
