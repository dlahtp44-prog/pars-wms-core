
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import openpyxl
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/엑셀-입고", response_class=HTMLResponse)
def page(request: Request):
    return templates.TemplateResponse("excel_inbound.html", {"request": request})

@router.post("/엑셀-입고")
def upload(file: UploadFile = File(...)):
    wb = openpyxl.load_workbook(file.file)
    ws = wb.active
    conn = get_db()
    cur = conn.cursor()
    success, fail = 0, 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        try:
            창고, 로케이션, 품번, 품명, LOT, 규격, 수량 = row
            cur.execute(
                """INSERT INTO 재고 VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(창고,로케이션,품번,LOT)
                DO UPDATE SET 수량=수량+excluded.수량""",
                (창고, 로케이션, 품번, 품명, LOT, 규격, int(수량))
            )
            cur.execute(
                """INSERT INTO 이력
                (구분,창고,품번,품명,LOT,규격,출발로케이션,도착로케이션,수량)
                VALUES('입고',?,?,?,?,?,?,?,?)""",
                (창고, 품번, 품명, LOT, 규격, "", 로케이션, int(수량))
            )
            success += 1
        except Exception:
            fail += 1
    conn.commit()
    conn.close()
    return {"success": success, "fail": fail}
