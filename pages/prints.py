from fastapi import APIRouter, Request, Query
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db
from app.utils.qr_utils import make_qr_png
from app.utils.pdf_utils import build_labels_pdf, build_simple_table_pdf, draw_qr_with_text

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/출력", response_class=HTMLResponse)
def print_hub(request: Request):
    return templates.TemplateResponse("prints.html", {"request": request})

@router.get("/qr.png")
def qr_png(data: str = Query(...)):
    return Response(content=make_qr_png(data), media_type="image/png")

def _product_draw(c, x, y, w, h, item):
    qr = make_qr_png(item["qr"])
    lines = [
        f'품번: {item["품번"]}',
        f'품명: {item["품명"]}',
        f'LOT: {item["LOT"]}',
        f'규격: {item["규격"]}',
        f'수량: {item["수량"]}',
        f'위치: {item.get("로케이션","")}',
    ]
    draw_qr_with_text(c, x, y, w, h, qr, lines)

@router.get("/print/제품라벨.pdf")
def print_product_labels(template: str = Query("LS-3108"), 창고: str | None = None, 로케이션: str | None = None,
                         limit: int = Query(14, ge=1, le=500)):
    conn = get_db(); cur = conn.cursor()
    sql = "SELECT 창고, 로케이션, 품번, 품명, LOT, 규격, 수량 FROM 재고 WHERE 1=1"
    params = []
    if 창고:
        sql += " AND 창고=?"; params.append(창고)
    if 로케이션:
        sql += " AND 로케이션=?"; params.append(로케이션)
    sql += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    items = [{
        "품번": r["품번"], "품명": r["품명"], "LOT": r["LOT"], "규격": r["규격"],
        "수량": r["수량"], "로케이션": r["로케이션"],
        "qr": f'ITEM|{r["품번"]}|{r["LOT"]}|{r["로케이션"]}'
    } for r in rows]
    pdf = build_labels_pdf(template, _product_draw, items)
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition":"inline; filename=product_labels.pdf"})

def _loc_draw(c, x, y, w, h, item):
    qr = make_qr_png(item["qr"])
    lines = [f'로케이션: {item["로케이션"]}', f'창고: {item["창고"]}']
    draw_qr_with_text(c, x, y, w, h, qr, lines)

@router.get("/print/로케이션QR.pdf")
def print_location_qr(template: str = Query("LS-3108"), 창고: str | None = None, 전체: int = Query(1, ge=0, le=1)):
    conn = get_db(); cur = conn.cursor()
    if 전체:
        if 창고:
            cur.execute("SELECT DISTINCT 창고, 로케이션 FROM 재고 WHERE 창고=? ORDER BY 로케이션", (창고,))
        else:
            cur.execute("SELECT DISTINCT 창고, 로케이션 FROM 재고 ORDER BY 창고, 로케이션")
    else:
        cur.execute("SELECT 'MAIN' as 창고, 'B01-01-01-A' as 로케이션")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    items = [{"창고": r["창고"], "로케이션": r["로케이션"], "qr": f"LOC|{r['창고']}|{r['로케이션']}"} for r in rows]
    pdf = build_labels_pdf(template, _loc_draw, items)
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition":"inline; filename=location_qr.pdf"})

@router.get("/print/재고.pdf")
def print_inventory(창고: str | None = None, 로케이션: str | None = None):
    conn = get_db(); cur = conn.cursor()
    sql = "SELECT 창고, 로케이션, 품번, 품명, LOT, 규격, 수량 FROM 재고 WHERE 1=1"
    params = []
    if 창고:
        sql += " AND 창고=?"; params.append(창고)
    if 로케이션:
        sql += " AND 로케이션=?"; params.append(로케이션)
    sql += " ORDER BY 창고, 로케이션, 품번, LOT"
    cur.execute(sql, params)
    rows = [list(map(str, r)) for r in cur.fetchall()]
    conn.close()
    pdf = build_simple_table_pdf("재고 현황", ["창고","로케이션","품번","품명","LOT","규격","수량"], rows)
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition":"inline; filename=inventory.pdf"})

@router.get("/print/이력.pdf")
def print_history(구분: str | None = None, limit: int = Query(300, ge=1, le=2000)):
    conn = get_db(); cur = conn.cursor()
    if 구분:
        cur.execute("SELECT 구분, 창고, 품번, 품명, LOT, 규격, 출발로케이션, 도착로케이션, 수량, created_at FROM 이력 WHERE 구분=? ORDER BY id DESC LIMIT ?",
                    (구분, limit))
    else:
        cur.execute("SELECT 구분, 창고, 품번, 품명, LOT, 규격, 출발로케이션, 도착로케이션, 수량, created_at FROM 이력 ORDER BY id DESC LIMIT ?",
                    (limit,))
    rows = [list(map(str, r)) for r in cur.fetchall()]
    conn.close()
    pdf = build_simple_table_pdf("이력", ["구분","창고","품번","품명","LOT","규격","출발","도착","수량","시간"], rows)
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition":"inline; filename=history.pdf"})
