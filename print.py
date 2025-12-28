
from fastapi import APIRouter
from fastapi.responses import Response
from app.db import get_db

router = APIRouter(prefix="/api/print")

@router.get("/inventory")
def print_inventory():
    from reportlab.pdfgen import canvas
    from io import BytesIO
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT 창고,로케이션,품번,품명,LOT,규격,수량 FROM 재고")
    rows = cur.fetchall()
    conn.close()

    buf = BytesIO()
    c = canvas.Canvas(buf)
    y = 800
    c.drawString(50, y, "재고 현황")
    y -= 20
    for r in rows:
        c.drawString(50, y, " | ".join(map(str, r)))
        y -= 15
    c.showPage()
    c.save()
    return Response(buf.getvalue(), media_type="application/pdf")

@router.get("/history")
def print_history():
    from reportlab.pdfgen import canvas
    from io import BytesIO
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT 구분,창고,품번,품명,LOT,규격,출발로케이션,도착로케이션,수량,created_at FROM 이력 ORDER BY id DESC LIMIT 200")
    rows = cur.fetchall()
    conn.close()

    buf = BytesIO()
    c = canvas.Canvas(buf)
    y = 800
    c.drawString(50, y, "이력 조회")
    y -= 20
    for r in rows:
        c.drawString(50, y, " | ".join(map(str, r)))
        y -= 15
    c.showPage()
    c.save()
    return Response(buf.getvalue(), media_type="application/pdf")
