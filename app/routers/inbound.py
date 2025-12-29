
from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from app.db import get_db

router = APIRouter(prefix="/api/inbound", tags=["inbound"])

@router.post("/excel")
def inbound_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="xlsx 파일만 업로드 가능합니다.")

    df = pd.read_excel(file.file)

    required = ["로케이션","품번","품명","LOT","규격","수량"]
    for col in required:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"{col} 컬럼이 없습니다.")

    conn = get_db()
    cur = conn.cursor()

    count = 0
    for _, row in df.iterrows():
        cur.execute("""
        INSERT INTO inbound
        (location, item_code, item_name, lot, spec, qty, memo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row["로케이션"],
            row["품번"],
            row["품명"],
            row["LOT"],
            row["규격"],
            int(row["수량"]),
            row.get("비고","")
        ))
        count += 1

    conn.commit()
    return {"result": "ok", "inserted": count}
