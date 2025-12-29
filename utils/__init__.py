import json

def parse_qr(text: str):
    """QR 문자열을 해석해서 dict로 반환.
    지원 형식:
      - JSON: {"location":"B01-01", ...}
      - LOC:xxxx  / ITEM:xxxx
      - 그 외: raw로 저장
    """
    t = (text or "").strip()
    if not t:
        return {"raw": ""}

    # JSON 형태
    if t.startswith("{") and t.endswith("}"):
        try:
            j = json.loads(t)
            if isinstance(j, dict):
                return {"raw": t, **j}
        except Exception:
            pass

    up = t.upper()
    if up.startswith("LOC:"):
        return {"raw": t, "location": t.split(":", 1)[1].strip()}
    if up.startswith("ITEM:"):
        return {"raw": t, "item_code": t.split(":", 1)[1].strip()}

    return {"raw": t}

from .qr_utils import make_qr_png
from .pdf_utils import build_labels_pdf, build_simple_table_pdf, draw_qr_with_text
