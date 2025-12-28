
from fastapi import APIRouter
from fastapi.responses import Response
from app.db import get_db

router = APIRouter(prefix="/api/label")

@router.get("/product")
def product_label():
    from reportlab.pdfgen import canvas
    from io import BytesIO

    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(50, 800, "제품 라벨 PDF (샘플)")
    c.showPage()
    c.save()

    return Response(buf.getvalue(), media_type="application/pdf")

@router.get("/location")
def location_label():
    from reportlab.pdfgen import canvas
    from io import BytesIO

    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(50, 800, "로케이션 라벨 PDF (샘플)")
    c.showPage()
    c.save()

    return Response(buf.getvalue(), media_type="application/pdf")
