from openpyxl import Workbook
from fastapi.responses import StreamingResponse
from io import BytesIO

def make_error_excel(headers, error_rows, filename="upload_error.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "ERRORS"
    ws.append(headers + ["오류사유"])

    for row, reason in error_rows:
        ws.append(list(row) + [reason])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
