import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

from .label_templates import TEMPLATES

def mm_to_pt(x_mm: float) -> float:
    return x_mm * mm

def build_labels_pdf(template_name: str, draw_label_fn, items):
    tpl = TEMPLATES.get(template_name)
    if not tpl:
        raise ValueError("Unknown template")
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    per_page = tpl.cols * tpl.rows
    for idx, item in enumerate(items):
        slot = idx % per_page
        if slot == 0 and idx > 0:
            c.showPage()

        r = slot // tpl.cols
        col = slot % tpl.cols

        x = mm_to_pt(tpl.margin_left_mm + col * (tpl.label_w_mm + tpl.gap_x_mm))
        y_top = mm_to_pt(tpl.page_h_mm - tpl.margin_top_mm - r * (tpl.label_h_mm + tpl.gap_y_mm))
        y = y_top - mm_to_pt(tpl.label_h_mm)

        w_pt = mm_to_pt(tpl.label_w_mm)
        h_pt = mm_to_pt(tpl.label_h_mm)

        draw_label_fn(c, x, y, w_pt, h_pt, item)

    c.save()
    return buf.getvalue()

def build_simple_table_pdf(title: str, columns: list[str], rows: list[list[str]]):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, height-20*mm, title)

    c.setFont("Helvetica", 9)
    x0 = 15*mm
    y = height-30*mm
    line_h = 5*mm
    col_w = (width-30*mm)/max(1, len(columns))

    for i, col in enumerate(columns):
        c.drawString(x0 + i*col_w, y, str(col)[:22])
    y -= line_h

    for r in rows:
        if y < 15*mm:
            c.showPage()
            y = height-20*mm
        for i, cell in enumerate(r):
            c.drawString(x0 + i*col_w, y, str(cell)[:22])
        y -= line_h

    c.save()
    return buf.getvalue()

def draw_qr_with_text(c, x, y, w, h, qr_png_bytes: bytes, lines: list[str]):
    qr_size = min(w, h) * 0.55
    qr_x = x + 3*mm
    qr_y = y + h - qr_size - 3*mm
    c.drawImage(ImageReader(io.BytesIO(qr_png_bytes)), qr_x, qr_y, qr_size, qr_size,
                preserveAspectRatio=True, mask='auto')

    tx = qr_x + qr_size + 3*mm
    ty = y + h - 5*mm
    c.setFont("Helvetica-Bold", 9)
    for i, line in enumerate(lines[:6]):
        c.drawString(tx, ty - i*10, line)
