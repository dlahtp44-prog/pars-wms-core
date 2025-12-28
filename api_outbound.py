from fastapi import APIRouter, Form, HTTPException
from app.db import get_db

router = APIRouter(prefix="/api/출고", tags=["출고"])

@router.post("")
def 출고(
    창고: str = Form(...),
    로케이션: str = Form(...),
    품번: str = Form(...),
    품명: str = Form(...),
    LOT: str = Form(...),
    규격: str = Form(...),
    수량: int = Form(...),
    비고: str = Form("")
):
    if 수량 <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT 수량 FROM 재고 WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?",
                (창고.strip(), 로케이션.strip(), 품번.strip(), LOT.strip()))
    row = cur.fetchone()
    if not row or int(row["수량"]) < int(수량):
        conn.close()
        raise HTTPException(status_code=404, detail="해당 재고가 없습니다.")

    cur.execute(
        "UPDATE 재고 SET 수량=수량-?, updated_at=datetime('now','localtime') WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?",
        (int(수량), 창고.strip(), 로케이션.strip(), 품번.strip(), LOT.strip())
    )
    cur.execute("DELETE FROM 재고 WHERE 수량<=0")

    cur.execute(
        """
        INSERT INTO 이력(구분, 창고, 품번, 품명, LOT, 규격, 출발로케이션, 도착로케이션, 수량, 비고)
        VALUES ('출고', ?, ?, ?, ?, ?, ?, '', ?, ?)
        """,
        (창고.strip(), 품번.strip(), 품명.strip(), LOT.strip(), 규격.strip(),
         로케이션.strip(), int(수량), (비고 or "").strip())
    )

    conn.commit(); conn.close()
    return {"result":"ok"}
