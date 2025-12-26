from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from openpyxl import load_workbook

from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/엑셀-입고", response_class=HTMLResponse)
def excel_inbound_page(request: Request):
    return templates.TemplateResponse(
        "excel_inbound.html",
        {"request": request}
    )


@router.post("/엑셀-입고", response_class=HTMLResponse)
def excel_inbound_upload(request: Request, file: UploadFile = File(...)):
    wb = load_workbook(file.file)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]

    required = ["창고", "로케이션", "품번", "품명", "LOT", "규격", "수량", "비고"]
    if headers != required:
        return templates.TemplateResponse(
            "excel_result.html",
            {
                "request": request,
                "errors": ["엑셀 헤더가 양식과 다릅니다."],
                "success": []
            }
        )

    success = []
    errors = []

    conn = get_db()
    cur = conn.cursor()

    for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고 = row

            if not 창고 or not 로케이션 or not 품번 or 수량 <= 0:
                raise ValueError("필수값 누락 또는 수량 오류")

            cur.execute("""
            INSERT INTO 재고(창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(창고, 로케이션, 품번, LOT)
            DO UPDATE SET
              수량 = 재고.수량 + excluded.수량,
              품명 = excluded.품명,
              규격 = excluded.규격,
              비고 = excluded.비고,
              updated_at = datetime('now','localtime')
            """, (창고, 로케이션, 품번, 품명, LOT, 규격, int(수량), 비고 or ""))

            cur.execute("""
            INSERT INTO 이력(구분, 창고, 품번, LOT, 출발로케이션, 도착로케이션, 수량, 비고)
            VALUES ('입고', ?, ?, ?, '', ?, ?, ?)
            """, (창고, 품번, LOT, 로케이션, int(수량), 비고 or ""))

            success.append(f"{idx}행 성공")

        except Exception as e:
            errors.append(f"{idx}행 실패: {str(e)}")

    conn.commit()
    conn.close()

    return templates.TemplateResponse(
        "excel_result.html",
        {
            "request": request,
            "success": success,
            "errors": errors
        }
    )
