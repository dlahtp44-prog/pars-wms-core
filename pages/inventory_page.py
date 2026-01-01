from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from app.core.paths import TEMPLATES_DIR
from fastapi.templating import Jinja2Templates
from app.db import get_db
import io
import openpyxl
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/page/inventory", response_class=HTMLResponse)
def page(request: Request, location: str = "", item_code: str = ""):
    where=[]
    params=[]
    if location:
        where.append("location LIKE ?")
        params.append(f"%{location}%")
    if item_code:
        where.append("item_code LIKE ?")
        params.append(f"%{item_code}%")
    where_sql=("WHERE " + " AND ".join(where)) if where else ""
    with get_db() as conn:
        rows = conn.execute(
            f"""SELECT location,item_code,item_name,lot,spec,brand,qty,updated_at,note
                 FROM inventory {where_sql}
                 ORDER BY location,item_code,lot""",
            params
        ).fetchall()
    return templates.TemplateResponse("inventory.html", {"request": request, "rows": rows, "location": location, "item_code": item_code})

@router.get("/page/inventory.xlsx")
def download(location: str = "", item_code: str = "", year: int | None = None, month: int | None = None):
    where=[]
    params=[]
    if location:
        where.append("location LIKE ?")
        params.append(f"%{location}%")
    if item_code:
        where.append("item_code LIKE ?")
        params.append(f"%{item_code}%")
    if year and month:
        start=f"{year:04d}-{month:02d}-01"
        # naive month end: next month -1 day
        if month==12:
            end=f"{year+1:04d}-01-01"
        else:
            end=f"{year:04d}-{month+1:02d}-01"
        where.append("updated_at >= ? AND updated_at < ?")
        params.extend([start, end])
    where_sql=("WHERE " + " AND ".join(where)) if where else ""
    with get_db() as conn:
        rows = conn.execute(
            f"""SELECT location,item_code,item_name,lot,spec,brand,qty,updated_at,note
                 FROM inventory {where_sql}
                 ORDER BY location,item_code,lot""",
            params
        ).fetchall()

    wb=openpyxl.Workbook()
    ws=wb.active
    ws.title="inventory"
    ws.append(["로케이션","품번","품명","LOT","규격","브랜드","수량","업데이트","비고"])
    for r in rows:
        ws.append([r["location"], r["item_code"], r["item_name"], r["lot"], r["spec"], r["brand"], r["qty"], r["updated_at"], r["note"]])
    bio=io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    filename="inventory.xlsx" if not (year and month) else f"inventory_{year:04d}{month:02d}.xlsx"
    headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
