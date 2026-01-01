from __future__ import annotations
from typing import List, Tuple, Any, Dict
from openpyxl import Workbook

def normalize_headers(headers: List[Any]) -> List[str]:
    return [("" if h is None else str(h)).strip() for h in headers]

def write_fail_xlsx(headers: List[str], failed_rows: List[Tuple[int, List[Any], str]], out_path: str) -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "failed"
    ws.append(headers + ["실패사유"])
    for rowno, rowvals, reason in failed_rows:
        vals = list(rowvals)
        while len(vals) < len(headers):
            vals.append("")
        ws.append(vals[:len(headers)] + [f"{rowno}행: {reason}"])
    wb.save(out_path)
    return out_path

def summarize(total: int, ok: int, fail: int, elapsed_sec: float) -> Dict[str, Any]:
    return {"total": total, "success": ok, "fail": fail, "elapsed_sec": round(elapsed_sec, 3)}
