from fastapi import APIRouter, Form, HTTPException
from app.db import get_db

router = APIRouter(prefix="/api/이동", tags=["이동"])


@router.post("")
def 이동(
    창고: str = Form(...),
    출발로케이션: str = Form(...),
    도착로케이션: str = Form(...),
    품번: str = Form(...),
    품명: str = Form(...),
    LOT: str = Form(...),
    규격: str = Form(...),
    수량: int = Form(...),
    비고: str = Form("")
):
    if 수량 <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

    conn = get_db()
    cur = conn.cursor()

    창고 = 창고.strip()
    출발로케이션 = 출발로케이션.strip()
    도착로케이션 = 도착로케이션.strip()
    품번 = 품번.strip()
    품명 = 품명.strip()
    LOT = LOT.strip()
    규격 = 규격.strip()
    비고 = (비고 or "").strip()

    if 출발로케이션 == 도착로케이션:
        conn.close()
        raise HTTPException(status_code=400, detail="출발/도착 로케이션이 같습니다.")

    # 출발 재고 확인
    cur.execute("""
    SELECT 수량 FROM 재고
    WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?
    """, (창고, 출발로케이션, 품번, LOT))
    row = cur.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="출발 로케이션에 재고가 없습니다.")

    현재수량 = int(row["수량"])
    if 현재수량 < 수량:
        conn.close()
        raise HTTPException(status_code=400, detail=f"재고 부족: 현재 {현재수량}, 요청 {수량}")

    # 1) 출발 차감
    남은수량 = 현재수량 - int(수량)
    if 남은수량 == 0:
        cur.execute("""
        DELETE FROM 재고
        WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?
        """, (창고, 출발로케이션, 품번, LOT))
    else:
        cur.execute("""
        UPDATE 재고
        SET 수량=?, updated_at=datetime('now','localtime')
        WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?
        """, (남은수량, 창고, 출발로케이션, 품번, LOT))

    # 2) 도착 합산 UPSERT
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
    """, (창고, 도착로케이션, 품번, 품명, LOT, 규격, int(수량), 비고))

    # 3) 이력 기록
    cur.execute("""
    INSERT INTO 이력(구분, 창고, 품번, LOT, 출발로케이션, 도착로케이션, 수량, 비고)
    VALUES ('이동', ?, ?, ?, ?, ?, ?, ?)
    """, (창고, 품번, LOT, 출발로케이션, 도착로케이션, int(수량), 비고))

    conn.commit()
    conn.close()
    return {"result": "ok"}
