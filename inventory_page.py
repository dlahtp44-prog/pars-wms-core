from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook
from app.db import get_db

router = APIRouter(prefix="/page/inventory", tags=["page-inventory"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("")
def inventory(request: Request, location: str = "", item_code: str = ""):
    conn = get_db()
    cur = conn.cursor()
    q = "SELECT location,item_code,item_name,lot,spec,brand,qty,note,updated_at FROM inventory WHERE 1=1"
    params=[]
    if location:
        q += " AND location LIKE ?"
        params.append(f"%{location}%")
    if item_code:
        q += " AND item_code LIKE ?"
        params.append(f"%{item_code}%")
    q += " ORDER BY updated_at DESC, location ASC"
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return templates.TemplateResponse("inventory.html", {"request": request, "title":"재고 조회", "rows": rows, "location": location, "item_code": item_code})

@router.get(".xlsx")
def inventory_xlsx(location: str = "", item_code: str = ""):
    conn = get_db()
    cur = conn.cursor()
    q = "SELECT location,item_code,item_name,lot,spec,brand,qty,note,updated_at FROM inventory WHERE 1=1"
    params=[]
    if location:
        q += " AND location LIKE ?"
        params.append(f"%{location}%")
    if item_code:
        q += " AND item_code LIKE ?"
        params.append(f"%{item_code}%")
    q += " ORDER BY updated_at DESC, location ASC"
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()

    wb=Workbook()
    ws=wb.active
    ws.title="inventory"
    ws.append(["로케이션","품번","품명","LOT","규격","브랜드","수량","비고","업데이트"])
    for r in rows:
        ws.append([r["location"], r["item_code"], r["item_name"], r["lot"], r["spec"], r["brand"], r["qty"], r["note"], r["updated_at"]])
    bio=BytesIO()
    wb.save(bio)
    bio.seek(0)

    filename="inventory.xlsx"
    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
