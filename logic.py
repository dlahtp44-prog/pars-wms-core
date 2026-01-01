from __future__ import annotations
from typing import Optional
from app.db import get_db, now_ts, ensure_location_for_write

def _get_inv(cur, location: str, item_code: str, lot: str, spec: str):
    return cur.execute(
        "SELECT * FROM inventory WHERE location=? AND item_code=? AND lot=? AND spec=?",
        (location, item_code, lot, spec),
    ).fetchone()

def inbound(location: str, item_code: str, item_name: str, lot: str, spec: str, qty: int, brand: str = "", note: str = "") -> None:
    if qty <= 0:
        raise ValueError("수량은 1 이상이어야 합니다.")
    ensure_location_for_write(location)

    ts = now_ts()
    with get_db() as conn:
        cur = conn.cursor()
        row = _get_inv(cur, location, item_code, lot, spec)
        if row:
            new_qty = int(row["qty"]) + int(qty)
            cur.execute(
                "UPDATE inventory SET item_name=?, brand=?, qty=?, note=?, updated_at=? WHERE id=?",
                (item_name, brand, new_qty, note, ts, row["id"]),
            )
        else:
            cur.execute(
                "INSERT INTO inventory(location,item_code,item_name,lot,spec,brand,qty,note,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (location, item_code, item_name, lot, spec, brand, int(qty), note, ts),
            )

        # 이벤트 테이블(선택): inbound
        cur.execute(
            "INSERT INTO inbound(ts,location,item_code,item_name,lot,spec,brand,qty,note) VALUES (?,?,?,?,?,?,?,?,?)",
            (ts, location, item_code, item_name, lot, spec, brand, int(qty), note),
        )

        # 통합 이력
        cur.execute(
            "INSERT INTO history(ts,kind,location,src_location,item_code,item_name,lot,spec,brand,qty,note) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (ts, "inbound", location, "", item_code, item_name, lot, spec, brand, int(qty), note),
        )
        conn.commit()

def outbound(location: str, item_code: str, item_name: str, lot: str, spec: str, qty: int, brand: str = "", note: str = "") -> None:
    if qty <= 0:
        raise ValueError("수량은 1 이상이어야 합니다.")
    ensure_location_for_write(location)

    ts = now_ts()
    with get_db() as conn:
        cur = conn.cursor()
        row = _get_inv(cur, location, item_code, lot, spec)
        if not row:
            raise ValueError("재고가 없습니다. (로케이션/품번/LOT/규격 확인)")
        cur_qty = int(row["qty"])
        new_qty = cur_qty - int(qty)
        if new_qty < 0:
            raise ValueError(f"출고 수량이 재고보다 큽니다. (재고:{cur_qty})")

        cur.execute(
            "UPDATE inventory SET item_name=?, brand=?, qty=?, note=?, updated_at=? WHERE id=?",
            (item_name, brand, new_qty, note, ts, row["id"]),
        )

        cur.execute(
            "INSERT INTO outbound(ts,location,item_code,item_name,lot,spec,brand,qty,note) VALUES (?,?,?,?,?,?,?,?,?)",
            (ts, location, item_code, item_name, lot, spec, brand, int(qty), note),
        )

        cur.execute(
            "INSERT INTO history(ts,kind,location,src_location,item_code,item_name,lot,spec,brand,qty,note) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (ts, "outbound", location, "", item_code, item_name, lot, spec, brand, int(qty), note),
        )
        conn.commit()

def move(src_location: str, dst_location: str, item_code: str, item_name: str, lot: str, spec: str, qty: int, brand: str = "", note: str = "") -> None:
    if qty <= 0:
        raise ValueError("수량은 1 이상이어야 합니다.")
    ensure_location_for_write(src_location)
    ensure_location_for_write(dst_location)

    ts = now_ts()
    with get_db() as conn:
        cur = conn.cursor()

        src_row = _get_inv(cur, src_location, item_code, lot, spec)
        if not src_row:
            raise ValueError("출발지 재고가 없습니다.")
        src_qty = int(src_row["qty"])
        if src_qty - int(qty) < 0:
            raise ValueError(f"이동 수량이 출발지 재고보다 큽니다. (재고:{src_qty})")

        # 출발지 차감
        cur.execute(
            "UPDATE inventory SET item_name=?, brand=?, qty=?, note=?, updated_at=? WHERE id=?",
            (item_name, brand, src_qty - int(qty), note, ts, src_row["id"]),
        )

        # 도착지 증가/생성
        dst_row = _get_inv(cur, dst_location, item_code, lot, spec)
        if dst_row:
            cur.execute(
                "UPDATE inventory SET item_name=?, brand=?, qty=?, note=?, updated_at=? WHERE id=?",
                (item_name, brand, int(dst_row["qty"]) + int(qty), note, ts, dst_row["id"]),
            )
        else:
            cur.execute(
                "INSERT INTO inventory(location,item_code,item_name,lot,spec,brand,qty,note,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (dst_location, item_code, item_name, lot, spec, brand, int(qty), note, ts),
            )

        cur.execute(
            "INSERT INTO moves(ts,src_location,dst_location,item_code,item_name,lot,spec,brand,qty,note) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (ts, src_location, dst_location, item_code, item_name, lot, spec, brand, int(qty), note),
        )

        cur.execute(
            "INSERT INTO history(ts,kind,location,src_location,item_code,item_name,lot,spec,brand,qty,note) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (ts, "move", dst_location, src_location, item_code, item_name, lot, spec, brand, int(qty), note),
        )
        conn.commit()
