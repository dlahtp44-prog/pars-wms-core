import json
def parse_qr(text: str):
    t = (text or "").strip()
    if not t:
        return {"raw": ""}
    if t.startswith("{") and t.endswith("}"):
        try:
            j = json.loads(t)
            return {"raw": t, **j}
        except Exception:
            pass
    if t.upper().startswith("LOC:"):
        return {"raw": t, "location": t.split(":",1)[1].strip()}
    if t.upper().startswith("ITEM:"):
        return {"raw": t, "item_code": t.split(":",1)[1].strip()}
    return {"raw": t, "location": t}
