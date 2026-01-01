from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import RedirectResponse
import pandas as pd

from app.db import get_db, now_kst_iso, ensure_location_for_write

router = APIRouter(prefix="/api/move", tags=["api-move"])


# -------------------------
# 수기 이동
# -------------------------
@router.post("")
def move_manual(
    location_from: str = Form(...),
    location_to: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form("")
):
    ensure_location_for_write(location_from)
    ensure_location_for_write(location_to)

    conn = get_db()
    cur = conn.cursor()

    # 출발지 차감
    cur.execute("""
        UPDATE inventory
        SET qty = qty - ?
        WHERE location_code=? AND item_code=? AND lot=?
    """, (qty, location_from, item_code, lot))

    # 도착지 증가
    cur.execute("""
        INSERT INTO inventory
        (location_code, item_code, item_name, lot, spec, qty, brand, updated_at)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        location_to, item_code, item_name,
        lot, spec, qty, brand, now_kst_iso()
    ))

    # 이력
    cur.execute("""
        INSERT INTO history
        (action_type, location_from, location_to, item_code, lot, qty, created_at)
        VALUES ('MOVE', ?, ?, ?, ?, ?, ?)
    """, (
        location_from, location_to,
        item_code, lot, qty, now_kst_iso()
    ))

    conn.commit()
    conn.close()

    return RedirectResponse("/page/move", status_code=303)


# -------------------------
# 엑셀 이동
# -------------------------
@router.post("/excel")
def move_excel(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    required = ["출발로케이션", "도착로케이션", "품번", "품명", "LOT", "규격", "수량", "브랜드"]
    for col in required:
        if col not in df.columns:
            return {"error": f"엑셀 컬럼 누락: {col}"}

    conn = get_db()
    cur = conn.cursor()

    for _, r in df.iterrows():
        qty = int(r["수량"])

        ensure_location_for_write(r["출발로케이션"])
        ensure_location_for_write(r["도착로케이션"])

        # 출발지 차감
        cur.execute("""
            UPDATE inventory
            SET qty = qty - ?
            WHERE location_code=? AND item_code=? AND lot=?
        """, (
            qty, r["출발로케이션"], r["품번"], r["LOT"]
        ))

        # 도착지 증가
        cur.execute("""
            INSERT INTO inventory
            (location_code, item_code, item_name, lot, spec, qty, brand, updated_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            r["도착로케이션"], r["품번"], r["품명"],
            r["LOT"], r["규격"], qty,
            r.get("브랜드",""), now_kst_iso()
        ))

        # 이력
        cur.execute("""
            INSERT INTO history
            (action_type, location_from, location_to, item_code, lot, qty, created_at)
            VALUES ('MOVE', ?, ?, ?, ?, ?, ?)
        """, (
            r["출발로케이션"], r["도착로케이션"],
            r["품번"], r["LOT"], qty, now_kst_iso()
        ))

    conn.commit()
    conn.close()

    return RedirectResponse("/page/move", status_code=303)
