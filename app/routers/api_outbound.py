from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import RedirectResponse
import pandas as pd

from app.db import get_db, now_kst_iso, ensure_location_for_write

router = APIRouter(prefix="/api/outbound", tags=["api-outbound"])


# -------------------------
# 수기 출고
# -------------------------
@router.post("")
def outbound_manual(
    location_code: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form("")
):
    ensure_location_for_write(location_code)

    conn = get_db()
    cur = conn.cursor()

    # 재고 차감
    cur.execute("""
        UPDATE inventory
        SET qty = qty - ?
        WHERE location_code=? AND item_code=? AND lot=?
    """, (qty, location_code, item_code, lot))

    # 이력 기록
    cur.execute("""
        INSERT INTO history
        (action_type, location_from, item_code, lot, qty, created_at)
        VALUES ('OUTBOUND', ?, ?, ?, ?, ?)
    """, (
        location_code, item_code, lot, qty, now_kst_iso()
    ))

    conn.commit()
    conn.close()

    return RedirectResponse("/page/outbound", status_code=303)


# -------------------------
# 엑셀 출고
# -------------------------
@router.post("/excel")
def outbound_excel(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    required = ["로케이션", "품번", "품명", "LOT", "규격", "수량", "브랜드"]
    for col in required:
        if col not in df.columns:
            return {"error": f"엑셀 컬럼 누락: {col}"}

    conn = get_db()
    cur = conn.cursor()

    for _, r in df.iterrows():
        ensure_location_for_write(r["로케이션"])

        qty = int(r["수량"])

        cur.execute("""
            UPDATE inventory
            SET qty = qty - ?
            WHERE location_code=? AND item_code=? AND lot=?
        """, (qty, r["로케이션"], r["품번"], r["LOT"]))

        cur.execute("""
            INSERT INTO history
            (action_type, location_from, item_code, lot, qty, created_at)
            VALUES ('OUTBOUND', ?, ?, ?, ?, ?)
        """, (
            r["로케이션"], r["품번"], r["LOT"],
            qty, now_kst_iso()
        ))

    conn.commit()
    conn.close()

    return RedirectResponse("/page/outbound", status_code=303)
