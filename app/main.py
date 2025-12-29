
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from app.db import get_db, init_db
import csv, io
from datetime import datetime

app = FastAPI(title="PARS WMS")

init_db()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.post("/api/inbound")
def api_inbound(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(""),
    lot: str = Form(""),
    spec: str = Form(""),
    brand: str = Form(""),
    qty: int = Form(...),
    memo: str = Form(""),
):
    db = get_db()

    db.execute("""
    INSERT INTO inventory
    (location, item_code, lot, spec, brand, qty, memo, updated_at)
    VALUES (?,?,?,?,?,?,?,datetime('now','localtime'))
    ON CONFLICT(location, item_code, lot, spec)
    DO UPDATE SET
      qty = qty + excluded.qty,
      brand = excluded.brand,
      memo = excluded.memo,
      updated_at = datetime('now','localtime')
    """, (location, item_code, lot, spec, brand, qty, memo))

    db.execute("""
    INSERT INTO history
    (location, item_code, lot, spec, brand, qty, memo, created_at, updated_at)
    VALUES (?,?,?,?,?,?,?,datetime('now','localtime'),datetime('now','localtime'))
    """, (location, item_code, lot, spec, brand, qty, memo))

    db.commit()
    db.close()
    return RedirectResponse("/page/inbound", status_code=303)


@app.get("/api/history/excel")
def history_excel():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    SELECT location, item_code, lot, spec, brand, qty, memo, created_at
    FROM history
    ORDER BY created_at DESC
    """)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["로케이션","품번","LOT","규격","브랜드","수량","비고","시간"])
    for r in cur.fetchall():
        writer.writerow(r)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition":"attachment; filename=history.csv"}
    )
