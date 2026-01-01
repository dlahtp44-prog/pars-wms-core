
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(prefix="/page/history")

@router.get("", response_class=HTMLResponse)
def page(request: Request):
    return request.app.state.templates.TemplateResponse("history.html", {"request": request})

@router.get("/xlsx")
def download():
    path = "static/history.xlsx"
    return FileResponse(path, filename="history.xlsx")
from fastapi.responses import StreamingResponse
import csv
import io
from app.db import get_db

@router.get("/history.xlsx")
def history_excel(
    limit: int = 200
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            action_type,
            location_from,
            location_to,
            item_code,
            lot,
            qty,
            created_at
        FROM history
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "구분","출발로케이션","도착로케이션","품번","LOT","수량","일시"
    ])
    for r in rows:
        writer.writerow([
            r["action_type"], r["location_from"], r["location_to"],
            r["item_code"], r["lot"], r["qty"], r["created_at"]
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=history.csv"}
    )
