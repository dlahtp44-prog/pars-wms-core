
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(prefix="/page/inventory")

@router.get("", response_class=HTMLResponse)
def page(request: Request):
    return request.app.state.templates.TemplateResponse("inventory.html", {"request": request})

@router.get("/xlsx")
def download():
    path = "static/inventory.xlsx"
    return FileResponse(path, filename="inventory.xlsx")

from fastapi.responses import StreamingResponse
import csv
import io
from app.db import get_db

@router.get("/inventory.xlsx")
def inventory_excel(
    location: str = "",
    item_code: str = ""
):
    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT
            location_code,
            item_code,
            item_name,
            lot,
            spec,
            qty,
            brand,
            updated_at
        FROM inventory
        WHERE 1=1
    """
    params = []

    if location:
        query += " AND location_code = ?"
        params.append(location)

    if item_code:
        query += " AND item_code = ?"
        params.append(item_code)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "로케이션","품번","품명","LOT","규격","수량","브랜드","수정일"
    ])
    for r in rows:
        writer.writerow([
            r["location_code"], r["item_code"], r["item_name"],
            r["lot"], r["spec"], r["qty"], r["brand"], r["updated_at"]
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory.csv"}
    )

