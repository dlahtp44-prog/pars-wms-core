from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook

from app.db import get_db

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/page/inventory")

@router.get("")
def page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request, "title": "재고 조회"})

@router.get(".xlsx")
def inventory_xlsx(
    location: str | None = Query(default=None),
    item_code: str | None = Query(default=None),
):
    where = []
    params = []
    if location:
        where.append("location LIKE ?")
        params.append(f"%{location}%")
    if item_code:
        where.append("item_code LIKE ?")
        params.append(f"%{item_code}%")
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    sql = f"""
    WITH all_moves AS (
        SELECT location, item_code, item_name, lot, spec, brand, qty AS delta_qty
        FROM inbound
        UNION ALL
        SELECT location, item_code, item_name, lot, spec, brand, -qty AS delta_qty
        FROM outbound
        UNION ALL
        SELECT src_location AS location, item_code, item_name, lot, spec, brand, -qty AS delta_qty
        FROM moves
        UNION ALL
        SELECT dst_location AS location, item_code, item_name, lot, spec, brand, qty AS delta_qty
        FROM moves
    )
    SELECT location, item_code, item_name, lot, spec, brand, SUM(delta_qty) AS qty
    FROM all_moves
    {where_sql}
    GROUP BY location, item_code, item_name, lot, spec, brand
    HAVING qty != 0
    ORDER BY location, item_code, lot
    """

    with get_db() as conn:
        cur = conn.cursor()
        rows = cur.execute(sql, params).fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "inventory"
    headers = ["location","item_code","item_name","lot","spec","brand","qty"]
    ws.append(headers)
    for r in rows:
        ws.append(list(r))

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="inventory.xlsx"'},
    )
