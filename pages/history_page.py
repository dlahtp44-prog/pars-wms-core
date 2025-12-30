from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook
from app.db import get_db

router = APIRouter(prefix="/page/history", tags=["page-history"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("")
def history(request: Request, limit: int = 200):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT ts,action,location,from_location,to_location,item_code,item_name,lot,spec,brand,qty,note FROM history ORDER BY id DESC LIMIT ?",
        (int(limit),),
    )
    rows = cur.fetchall()
    conn.close()
    return templates.TemplateResponse("history.html", {"request": request, "title":"이력조회", "rows": rows, "limit": limit})

@router.get(".xlsx")
def history_xlsx(limit: int = 200):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT ts,action,location,from_location,to_location,item_code,item_name,lot,spec,brand,qty,note FROM history ORDER BY id DESC LIMIT ?",
        (int(limit),),
    )
    rows = cur.fetchall()
    conn.close()

    wb=Workbook()
    ws=wb.active
    ws.title="history"
    ws.append(["시간","구분","로케이션","출발","도착","품번","품명","LOT","규격","브랜드","수량","비고"])
    for r in rows:
        ws.append([r["ts"], r["action"], r["location"], r["from_location"], r["to_location"], r["item_code"], r["item_name"], r["lot"], r["spec"], r["brand"], r["qty"], r["note"]])
    bio=BytesIO()
    wb.save(bio)
    bio.seek(0)

    filename="history.xlsx"
    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
