from fastapi import APIRouter, Form, HTTPException
from app.db import get_db

router = APIRouter(prefix="/api/입고", tags=["입고"])

@router.post("")
def 입고(
    창고: str = Form(...),
    로케이션: str = Form(...),
    품번: str = Form(...),
    품명: str = Form(...),
    LOT: str = Form(...),
    규격: str = Form(...),
    수량: int = Form(...),
    비고: str = Form("")
):
    if int(수량) <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

    창고 = (창고 or "").strip()
    로케이션 = (로케이션 or "").strip()
    품번 = (품번 or "").strip()
    품명 = (품명 or "").strip()
    LOT = (LOT or "").strip()
    규격 = (규격 or "").strip()
    비고 = (비고 or "").strip()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO 재고(창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(창고, 로케이션, 품번, LOT)
    DO UPDATE SET
      수량 = 재고.수량 + excluded.수량,
      품명 = excluded.품명,
      규격 = excluded.규격,
      비고 = excluded.비고,
      updated_at = datetime('now','localtime')
    """, (창고, 로케이션, 품번, 품명, LOT, 규격, int(수량), 비고))

    cur.execute("""
    INSERT INTO 이력(구분, 창고, 품번, LOT, 출발로케이션, 도착로케이션, 수량, 비고)
    VALUES ('입고', ?, ?, ?, '', ?, ?, ?)
    """, (창고, 품번, LOT, 로케이션, int(수량), 비고))

    conn.commit()
    conn.close()
    return {"result": "ok"}
