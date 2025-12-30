from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook

from app.db import get_db

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/page/history")

@router.get("")
def page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request, "title": "이력조회"})

@router.get(".xlsx")
def history_xlsx(limit: int = Query(default=200)):
    limit = max(1, min(20000, limit))
    with get_db() as conn:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT ts, kind, location, src_location, item_code, item_name, lot, spec, brand, qty, note FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "history"
    headers = ["ts","kind","location","src_location","item_code","item_name","lot","spec","brand","qty","note"]
    ws.append(headers)
    for r in rows:
        ws.append(list(r))

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="history.xlsx"'},
    )
