def parse_qr(raw: str) -> dict:
    """
    QR 예:
    type=LOC&warehouse=MAIN&location=D01-01
    """
    result = {}
    if not raw:
        return result

    for part in raw.split("&"):
        if "=" not in part:
            continue

        key, value = part.split("=", 1)
        key = key.strip().lower()
        value = value.strip()

        # type은 무시
        if key == "type":
            continue

        result[key] = value

    return result
