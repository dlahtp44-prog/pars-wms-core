from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import RedirectResponse
import pandas as pd
from app.db import get_db, now_kst_iso, ensure_location_for_write

router = APIRouter(prefix="/api/inbound", tags=["api-inbound"])


# -------------------------
# 수기 입고
# -------------------------
@router.post("")
def inbound_manual(
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

    cur.execute("""
        INSERT INTO inventory
        (location_code, item_code, item_name, lot, spec, qty, brand, updated_at)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        location_code, item_code, item_name,
        lot, spec, qty, brand, now_kst_iso()
    ))

    cur.execute("""
        INSERT INTO history
        (action_type, location_to, item_code, lot, qty, created_at)
        VALUES ('INBOUND', ?, ?, ?, ?, ?)
    """, (location_code, item_code, lot, qty, now_kst_iso()))

    conn.commit()
    conn.close()

    return RedirectResponse("/page/inbound", status_code=303)


# -------------------------
# 엑셀 입고
# -------------------------
@router.post("/excel")
def inbound_excel(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    required = ["로케이션", "품번", "품명", "LOT", "규격", "수량", "브랜드"]
    for col in required:
        if col not in df.columns:
            return {"error": f"엑셀 컬럼 누락: {col}"}

    conn = get_db()
    cur = conn.cursor()

    for _, r in df.iterrows():
        ensure_location_for_write(r["로케이션"])

        cur.execute("""
            INSERT INTO inventory
            (location_code, item_code, item_name, lot, spec, qty, brand, updated_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            r["로케이션"], r["품번"], r["품명"],
            r["LOT"], r["규격"], int(r["수량"]),
            r.get("브랜드",""), now_kst_iso()
        ))

        cur.execute("""
            INSERT INTO history
            (action_type, location_to, item_code, lot, qty, created_at)
            VALUES ('INBOUND', ?, ?, ?, ?, ?)
        """, (
            r["로케이션"], r["품번"], r["LOT"],
            int(r["수량"]), now_kst_iso()
        ))

    conn.commit()
    conn.close()

    return RedirectResponse("/page/inbound", status_code=303)
