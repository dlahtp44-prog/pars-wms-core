from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from app.core.paths import TEMPLATES_DIR
from fastapi.templating import Jinja2Templates
from app.db import get_db
import io
import openpyxl

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/page/history", response_class=HTMLResponse)
def page(request: Request, limit: int = 200):
    limit=max(1, min(2000, int(limit)))
    with get_db() as conn:
        rows = conn.execute(
            "SELECT ts,kind,location,src_location,item_code,item_name,lot,spec,brand,qty,note FROM history ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return templates.TemplateResponse("history.html", {"request": request, "rows": rows, "limit": limit})

@router.get("/page/history.xlsx")
def download(limit: int = 200, year: int | None = None, month: int | None = None):
    limit=max(1, min(2000, int(limit)))
    where=[]
    params=[]
    if year and month:
        start=f"{year:04d}-{month:02d}-01"
        if month==12:
            end=f"{year+1:04d}-01-01"
        else:
            end=f"{year:04d}-{month+1:02d}-01"
        where.append("ts >= ? AND ts < ?")
        params.extend([start, end])
    where_sql=("WHERE " + " AND ".join(where)) if where else ""
    sql=f"SELECT ts,kind,location,src_location,item_code,item_name,lot,spec,brand,qty,note FROM history {where_sql} ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        rows=conn.execute(sql, params).fetchall()

    wb=openpyxl.Workbook()
    ws=wb.active
    ws.title="history"
    ws.append(["시간","구분","로케이션","출발","품번","품명","LOT","규격","브랜드","수량","비고"])
    for r in rows:
        ws.append([r["ts"], r["kind"], r["location"], r["src_location"], r["item_code"], r["item_name"], r["lot"], r["spec"], r["brand"], r["qty"], r["note"]])
    bio=io.BytesIO()
    wb.save(bio); bio.seek(0)
    filename="history.xlsx" if not (year and month) else f"history_{year:04d}{month:02d}.xlsx"
    headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
