
from fastapi import APIRouter, Form
from app.db import get_db
router = APIRouter(prefix="/api/입고")

@router.post("")
def inbound(
    창고: str = Form(...),
    로케이션: str = Form(...),
    품번: str = Form(...),
    품명: str = Form(...),
    LOT: str = Form(...),
    규격: str = Form(...),
    수량: int = Form(...)
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO 재고 VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(창고,로케이션,품번,LOT)
        DO UPDATE SET 수량=수량+excluded.수량""",
        (창고,로케이션,품번,품명,LOT,규격,수량)
    )
    cur.execute(
        """INSERT INTO 이력
        (구분,창고,품번,품명,LOT,규격,출발로케이션,도착로케이션,수량)
        VALUES('입고',?,?,?,?,?,?,?,?)""",
        (창고,품번,품명,LOT,규격,"",로케이션,수량)
    )
    conn.commit(); conn.close()
    return {"result":"ok"}
