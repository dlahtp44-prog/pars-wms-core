from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openpyxl import load_workbook
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/엑셀-이동", response_class=HTMLResponse)
def page(request: Request):
    return templates.TemplateResponse("excel_move.html", {"request": request})

@router.post("/엑셀-이동", response_class=HTMLResponse)
def upload(request: Request, file: UploadFile = File(...)):
    wb = load_workbook(file.file); ws = wb.active
    headers = [c.value for c in ws[1]]
    need = ["창고","출발로케이션","도착로케이션","품번","품명","LOT","규격","수량","비고"]
    ok, fail = [], []
    if headers != need:
        return templates.TemplateResponse("excel_result.html",
            {"request":request,"success":[], "errors":["헤더 불일치"]})

    conn = get_db(); cur = conn.cursor()
    for i,row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            창고, 출발, 도착, 품번, 품명, LOT, 규격, 수량, 비고 = row
            if not all([창고,출발,도착,품번,품명,LOT,규격]) or int(수량)<=0:
                raise ValueError("필수값/수량 오류")
            cur.execute("""
              SELECT 수량 FROM 재고
              WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?
            """,(창고,출발,품번,LOT))
            r = cur.fetchone()
            if not r or r[0] < int(수량):
                raise ValueError("출발 로케이션에 재고가 없습니다.")
            # 차감
            cur.execute("""
              UPDATE 재고 SET 수량=수량-?
              WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?
            """,(int(수량),창고,출발,품번,LOT))
            # 도착 UPSERT
            cur.execute("""
              INSERT INTO 재고(창고,로케이션,품번,품명,LOT,규격,수량,비고)
              VALUES(?,?,?,?,?,?,?,?)
              ON CONFLICT(창고,로케이션,품번,LOT)
              DO UPDATE SET 수량=재고.수량+excluded.수량
            """,(창고,도착,품번,품명,LOT,규격,int(수량),비고 or ""))
            # 이력
            cur.execute("""
              INSERT INTO 이력(구분,창고,품번,LOT,출발로케이션,도착로케이션,수량,비고)
              VALUES('이동',?,?,?,?,?, ?,?)
            """,(창고,품번,LOT,출발,도착,int(수량),비고 or ""))
            ok.append(f"{i}행 성공")
        except Exception as e:
            fail.append(f"{i}행 실패: {e}")
    conn.commit(); conn.close()
    return templates.TemplateResponse("excel_result.html",
        {"request":request,"success":ok,"errors":fail})
