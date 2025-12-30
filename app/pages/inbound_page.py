from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR
from fastapi.responses import RedirectResponse
from app.logic import inbound
from app.core.downloads import create_token
from .excel_utils import read_xlsx_rows, make_error_xlsx, to_str, to_int

router = APIRouter(prefix="/page/inbound", tags=["page-inbound"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("")
def inbound_form(request: Request, msg: str = ""):
    return templates.TemplateResponse("inbound.html", {"request": request, "title": "입고등록", "msg": msg})

@router.post("/save")
def inbound_save(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form(""),
    note: str = Form(""),
):
    inbound(location, item_code, item_name, lot, spec, int(qty), brand, note)
    return RedirectResponse(url="/page/inbound?msg=저장완료", status_code=303)

@router.post("/excel")
async def inbound_excel(request: Request, file: UploadFile = File(...)):
    content = await file.read()
    header, rows = read_xlsx_rows(content)

    required = ["로케이션","품번","품명","LOT","규격","수량"]
    ok=0
    bad=[]
    for r in rows:
        try:
            for k in required:
                if to_str(r.get(k,""))=="":
                    raise ValueError(f"{k} 누락")
            location = to_str(r["로케이션"])
            item_code = to_str(r["품번"])
            item_name = to_str(r["품명"])
            lot = to_str(r["LOT"])
            spec = to_str(r["규격"])
            qty = to_int(r["수량"])
            brand = to_str(r.get("브랜드",""))
            note = to_str(r.get("비고",""))
            inbound(location, item_code, item_name, lot, spec, qty, brand, note)
            ok += 1
        except Exception as e:
            rr=dict(r)
            rr["에러"]=str(e)
            bad.append(rr)

    token=None
    if bad:
        err_bytes = make_error_xlsx(header, bad)
        token = create_token(err_bytes, filename="inbound_errors.xlsx", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    return templates.TemplateResponse("excel_result.html", {
        "request": request,
        "title": "입고 엑셀 업로드 결과",
        "ok_count": ok,
        "fail_count": len(bad),
        "download_token": token,
    })
