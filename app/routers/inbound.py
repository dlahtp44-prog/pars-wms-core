from fastapi import APIRouter, Form, HTTPException
from app.db import get_db

router = APIRouter(
    prefix="/api/입고",
    tags=["입고"]
)

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
    # 1️⃣ 유효성 검사
    if 수량 <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

    try:
        conn = get_db()
        cur = conn.cursor()

        # 2️⃣ 재고 테이블 UPSERT (합산)
        cur.execute("""
        INSERT INTO 재고 (
            창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(창고, 로케이션, 품번, LOT)
        DO UPDATE SET
            수량 = 재고.수량 + excluded.수량,
            품명 = excluded.품명,
            규격 = excluded.규격,
            비고 = excluded.비고
        """, (
            창고.strip(),
            로케이션.strip(),
            품번.strip(),
            품명.strip(),
            LOT.strip(),
            규격.strip(),
            int(수량),
            비고.strip()
        ))

        # 3️⃣ 이력 테이블 기록
        cur.execute("""
        INSERT INTO 이력 (
            구분,
            창고,
            품번,
            LOT,
            출발로케이션,
            도착로케이션,
            수량,
            비고
        )
        VALUES (
            '입고',
            ?,
            ?,
            ?,
            '',
            ?,
            ?,
            ?
        )
        """, (
            창고.strip(),
            품번.strip(),
            LOT.strip(),
            로케이션.strip(),
            int(수량),
            비고.strip()
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()

    return {
        "result": "ok",
        "message": "입고 처리 완료",
        "품번": 품번,
        "LOT": LOT,
        "수량": 수량,
        "로케이션": 로케이션
    }
