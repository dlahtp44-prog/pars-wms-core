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
    if 출발로케이션.strip() == 도착로케이션.strip():
        raise HTTPException(status_code=400, detail="출발/도착 로케이션이 같습니다.")

    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT 수량 FROM 재고 WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?",
                (창고.strip(), 출발로케이션.strip(), 품번.strip(), LOT.strip()))
    row = cur.fetchone()
    if not row or int(row["수량"]) < int(수량):
        conn.close()
        raise HTTPException(status_code=404, detail="출발 로케이션에 재고가 없습니다.")

    cur.execute(
        "UPDATE 재고 SET 수량=수량-?, updated_at=datetime('now','localtime') WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?",
        (int(수량), 창고.strip(), 출발로케이션.strip(), 품번.strip(), LOT.strip())
    )
    cur.execute("DELETE FROM 재고 WHERE 수량<=0")

    cur.execute(
        """
        INSERT INTO 재고(창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(창고, 로케이션, 품번, LOT)
        DO UPDATE SET
          수량 = 재고.수량 + excluded.수량,
          품명 = excluded.품명,
          규격 = excluded.규격,
          비고 = excluded.비고,
          updated_at = datetime('now','localtime')
        """,
        (창고.strip(), 도착로케이션.strip(), 품번.strip(), 품명.strip(), LOT.strip(), 규격.strip(), int(수량), (비고 or "").strip())
    )

    cur.execute(
        """
        INSERT INTO 이력(구분, 창고, 품번, 품명, LOT, 규격, 출발로케이션, 도착로케이션, 수량, 비고)
        VALUES ('이동', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (창고.strip(), 품번.strip(), 품명.strip(), LOT.strip(), 규격.strip(),
         출발로케이션.strip(), 도착로케이션.strip(), int(수량), (비고 or "").strip())
    )

    conn.commit(); conn.close()
    return {"result":"ok"}
