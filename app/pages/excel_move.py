
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import openpyxl
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/엑셀-이동", response_class=HTMLResponse)
def page(request: Request):
    return templates.TemplateResponse("excel_move.html", {"request": request})

@router.post("/엑셀-이동")
def upload(file: UploadFile = File(...)):
    wb = openpyxl.load_workbook(file.file)
    ws = wb.active
    conn = get_db()
    cur = conn.cursor()
    success, fail = 0, 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        try:
            창고, 출발, 도착, 품번, 품명, LOT, 규격, 수량 = row

            cur.execute(
                "SELECT 수량 FROM 재고 WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?",
                (창고, 출발, 품번, LOT)
            )
            r = cur.fetchone()
            if not r or int(r[0]) < int(수량):
                raise Exception("재고 부족")

            cur.execute(
                "UPDATE 재고 SET 수량=수량-? WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?",
                (int(수량), 창고, 출발, 품번, LOT)
            )
            cur.execute("DELETE FROM 재고 WHERE 수량<=0")

            cur.execute(
                """INSERT INTO 재고 VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(창고,로케이션,품번,LOT)
                DO UPDATE SET 수량=수량+excluded.수량""",
                (창고, 도착, 품번, 품명, LOT, 규격, int(수량))
            )

            cur.execute(
                """INSERT INTO 이력
                (구분,창고,품번,품명,LOT,규격,출발로케이션,도착로케이션,수량)
                VALUES('이동',?,?,?,?,?,?,?,?)""",
                (창고, 품번, 품명, LOT, 규격, 출발, 도착, int(수량))
            )
            success += 1
        except Exception:
            fail += 1

    conn.commit()
    conn.close()
    return {"success": success, "fail": fail}
