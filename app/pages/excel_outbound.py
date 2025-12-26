from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openpyxl import load_workbook
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/엑셀-출고", response_class=HTMLResponse)
def page(request: Request):
    return templates.TemplateResponse("excel_outbound.html", {"request": request})

@router.post("/엑셀-출고", response_class=HTMLResponse)
def upload(request: Request, file: UploadFile = File(...)):
    wb = load_workbook(file.file); ws = wb.active
    headers = [c.value for c in ws[1]]
    need = ["창고","로케이션","품번","LOT","수량","비고"]
    ok, fail = [], []
    if headers != need:
        return templates.TemplateResponse("excel_result.html",
            {"request":request,"success":[], "errors":["헤더 불일치"]})

    conn = get_db(); cur = conn.cursor()
    for i,row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            창고, 로케이션, 품번, LOT, 수량, 비고 = row
            if not 창고 or not 로케이션 or not 품번 or not LOT or int(수량) <= 0:
                raise ValueError("필수값/수량 오류")
            cur.execute("""
              SELECT 수량 FROM 재고
              WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?
            """,(창고,로케이션,품번,LOT))
            r = cur.fetchone()
            if not r or r[0] < int(수량):
                raise ValueError("해당 재고가 없습니다.")
            # 차감
            cur.execute("""
              UPDATE 재고 SET 수량=수량-?
              WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?
            """,(int(수량),창고,로케이션,품번,LOT))
            # 이력
            cur.execute("""
              INSERT INTO 이력(구분,창고,품번,LOT,출발로케이션,도착로케이션,수량,비고)
              VALUES('출고',?,?,?,?,?, ?,?)
            """,(창고,품번,LOT,로케이션,"",int(수량),비고 or ""))
            ok.append(f"{i}행 성공")
        except Exception as e:
            fail.append(f"{i}행 실패: {e}")
    conn.commit(); conn.close()
    return templates.TemplateResponse("excel_result.html",
        {"request":request,"success":ok,"errors":fail})
