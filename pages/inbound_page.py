from fastapi import APIRouter, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import tempfile
import time

from app.db import get_db, now_ts
from app.core.excel_import import read_xlsx_rows, map_columns, get, get_int
from app.core.excel_utils import write_fail_xlsx, summarize
from app.core.downloads import register_file

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(prefix="/page/inbound")

@router.get("")
def page(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request, "title": "입고등록"})

@router.post("/excel", response_class=HTMLResponse)
async def inbound_excel(request: Request, file: UploadFile = File(...)):
    t0 = time.time()
    if not (file.filename or "").lower().endswith(".xlsx"):
        return templates.TemplateResponse("excel_result.html", {
            "request": request,
            "ok": False,
            "summary": {"total": 0, "success": 0, "fail": 1, "elapsed_sec": 0},
            "message": "엑셀(xlsx) 파일만 업로드 가능합니다.",
            "download_url": None,
            "retry_url": "/page/inbound",
        })

    tmpdir = tempfile.mkdtemp(prefix="pars_excel_")
    xlsx_path = os.path.join(tmpdir, "upload.xlsx")
    with open(xlsx_path, "wb") as f:
        f.write(await file.read())

    headers, data_rows = read_xlsx_rows(xlsx_path)
    colmap = map_columns(headers)

    required = ["location", "item_code", "item_name", "lot", "spec", "qty"]
    missing = [k for k in required if k not in colmap]
    if missing:
        return templates.TemplateResponse("excel_result.html", {
            "request": request,
            "ok": False,
            "summary": {"total": 0, "success": 0, "fail": 1, "elapsed_sec": round(time.time()-t0,3)},
            "message": f"필수 컬럼이 없습니다: {', '.join(missing)} (예: 로케이션, 품번, 품명, LOT, 규격, 수량)",
            "download_url": None,
            "retry_url": "/page/inbound",
        })

    failed = []
    ok = 0
    with get_db() as conn:
        cur = conn.cursor()
        for idx, row in enumerate(data_rows, start=2):  # excel line no
            try:
                location = get(row, colmap, "location")
                item_code = get(row, colmap, "item_code")
                item_name = get(row, colmap, "item_name")
                lot = get(row, colmap, "lot")
                spec = get(row, colmap, "spec")
                brand = get(row, colmap, "brand")
                note = get(row, colmap, "note")
                qty = get_int(row, colmap, "qty")
                if not all([location, item_code, item_name, lot, spec]) or qty <= 0:
                    raise ValueError("필수값 누락 또는 수량이 1 미만입니다.")
                ts = now_ts()
                cur.execute(
                    "INSERT INTO inbound(ts,location,item_code,item_name,lot,spec,brand,qty,note) VALUES(?,?,?,?,?,?,?,?,?)",
                    (ts, location, item_code, item_name, lot, spec, brand, qty, note),
                )
                cur.execute(
                    "INSERT INTO history(ts,kind,location,src_location,item_code,item_name,lot,spec,brand,qty,note) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (ts, "inbound", location, "", item_code, item_name, lot, spec, brand, qty, note),
                )
                ok += 1
            except Exception as e:
                failed.append((idx, row, str(e)))

    total = len(data_rows)
    fail = len(failed)
    download_url = None
    if fail:
        out_path = os.path.join(tmpdir, f"inbound_failed_{int(time.time())}.xlsx")
        write_fail_xlsx(headers, failed, out_path)
        token = register_file(out_path, ttl_seconds=1800)
        download_url = f"/download/{token}"

    summ = summarize(total, ok, fail, time.time()-t0)
    return templates.TemplateResponse("excel_result.html", {
        "request": request,
        "ok": (fail == 0),
        "summary": summ,
        "message": "업로드 완료" if fail == 0 else "일부 행이 실패했습니다. 실패행 엑셀을 내려받아 수정 후 재업로드하세요.",
        "download_url": download_url,
        "retry_url": "/page/inbound",
    })
