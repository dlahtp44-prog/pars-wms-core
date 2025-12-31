def add_move(from_location, to_location, item_code, item_name, lot, spec, brand, qty, note=""):
    """
    재고 이동 처리 + 이력(move) 기록
    """

    # 1️⃣ 출발지 재고 차감
    _upsert_inventory(
        from_location,
        item_code,
        item_name,
        lot,
        spec,
        brand,
        -int(qty),
        note
    )

    # 2️⃣ 도착지 재고 증가
    _upsert_inventory(
        to_location,
        item_code,
        item_name,
        lot,
        spec,
        brand,
        int(qty),
        note
    )

    # 3️⃣ 이동 이력 기록 (🔥 이게 핵심)
    _add_history(
        "move",          # type
        "",              # location (move는 비움)
        from_location,   # 출발
        to_location,     # 도착
        item_code,
        item_name,
        lot,
        spec,
        brand,
        int(qty),
        note or "QR 이동"
    )
