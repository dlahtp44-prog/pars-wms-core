from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR
from fastapi.responses import RedirectResponse
from app.logic import move
from app.core.downloads import create_token
from .excel_utils import read_xlsx_rows, make_error_xlsx, to_str, to_int

router = APIRouter(prefix="/page/move", tags=["page-move"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("")
def move_form(request: Request, msg: str = ""):
    return templates.TemplateResponse("move.html", {"request": request, "title": "이동등록", "msg": msg})

@router.post("/save")
def move_save(
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form(""),
    note: str = Form(""),
):
    move(from_location, to_location, item_code, item_name, lot, spec, int(qty), brand, note)
    return RedirectResponse(url="/page/move?msg=처리완료", status_code=303)

@router.post("/excel")
async def move_excel(request: Request, file: UploadFile = File(...)):
    content = await file.read()
    header, rows = read_xlsx_rows(content)

    required = ["출발로케이션","도착로케이션","품번","품명","LOT","규격","수량"]
    ok=0
    bad=[]
    for r in rows:
        try:
            for k in required:
                if to_str(r.get(k,""))=="":
                    raise ValueError(f"{k} 누락")
            from_location = to_str(r["출발로케이션"])
            to_location = to_str(r["도착로케이션"])
            item_code = to_str(r["품번"])
            item_name = to_str(r["품명"])
            lot = to_str(r["LOT"])
            spec = to_str(r["규격"])
            qty = to_int(r["수량"])
            brand = to_str(r.get("브랜드",""))
            note = to_str(r.get("비고",""))
            move(from_location, to_location, item_code, item_name, lot, spec, qty, brand, note)
            ok += 1
        except Exception as e:
            rr=dict(r)
            rr["에러"]=str(e)
            bad.append(rr)

    token=None
    if bad:
        err_bytes = make_error_xlsx(header, bad)
        token = create_token(err_bytes, filename="move_errors.xlsx", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    return templates.TemplateResponse("excel_result.html", {
        "request": request,
        "title": "이동 엑셀 업로드 결과",
        "ok_count": ok,
        "fail_count": len(bad),
        "download_token": token,
    })
