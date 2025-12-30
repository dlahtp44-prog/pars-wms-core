from __future__ import annotations
from typing import Optional, Tuple
from .db import get_db, now_kst_iso

def _get_inventory_row(cur, location: str, item_code: str, lot: str, spec: str):
    cur.execute(
        "SELECT * FROM inventory WHERE location=? AND item_code=? AND lot=? AND spec=?",
        (location, item_code, lot, spec),
    )
    return cur.fetchone()

def inbound(location: str, item_code: str, item_name: str, lot: str, spec: str, qty: int, brand: str = "", note: str = "") -> None:
    if qty <= 0:
        raise ValueError("수량은 1 이상이어야 합니다.")
    conn = get_db()
    cur = conn.cursor()
    ts = now_kst_iso()

    row = _get_inventory_row(cur, location, item_code, lot, spec)
    if row:
        new_qty = int(row["qty"]) + qty
        cur.execute(
            "UPDATE inventory SET item_name=?, brand=?, qty=?, note=?, updated_at=? WHERE id=?",
            (item_name, brand, new_qty, note, ts, row["id"]),
        )
    else:
        cur.execute(
            "INSERT INTO inventory(location,item_code,item_name,lot,spec,brand,qty,note,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (location, item_code, item_name, lot, spec, brand, qty, note, ts),
        )

    cur.execute(
        "INSERT INTO history(ts,action,location,item_code,item_name,lot,spec,brand,qty,note) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (ts, "inbound", location, item_code, item_name, lot, spec, brand, qty, note),
    )
    conn.commit()
    conn.close()

def outbound(location: str, item_code: str, item_name: str, lot: str, spec: str, qty: int, brand: str = "", note: str = "") -> None:
    if qty <= 0:
        raise ValueError("수량은 1 이상이어야 합니다.")
    conn = get_db()
    cur = conn.cursor()
    ts = now_kst_iso()

    row = _get_inventory_row(cur, location, item_code, lot, spec)
    if not row:
        conn.close()
        raise ValueError("재고가 없습니다. (로케이션/품번/LOT/규격 확인)")
    cur_qty = int(row["qty"])
    new_qty = cur_qty - qty
    if new_qty < 0:
        conn.close()
        raise ValueError(f"출고 수량이 재고보다 큽니다. (재고:{cur_qty})")
    cur.execute(
        "UPDATE inventory SET item_name=?, brand=?, qty=?, note=?, updated_at=? WHERE id=?",
        (item_name, brand, new_qty, note, ts, row["id"]),
    )

    cur.execute(
        "INSERT INTO history(ts,action,location,item_code,item_name,lot,spec,brand,qty,note) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (ts, "outbound", location, item_code, item_name, lot, spec, brand, qty, note),
    )
    conn.commit()
    conn.close()

def move(from_location: str, to_location: str, item_code: str, item_name: str, lot: str, spec: str, qty: int, brand: str = "", note: str = "") -> None:
    if qty <= 0:
        raise ValueError("수량은 1 이상이어야 합니다.")
    if from_location == to_location:
        raise ValueError("출발/도착 로케이션이 같습니다.")
    conn = get_db()
    cur = conn.cursor()
    ts = now_kst_iso()

    from_row = _get_inventory_row(cur, from_location, item_code, lot, spec)
    if not from_row:
        conn.close()
        raise ValueError("출발 로케이션에 재고가 없습니다.")
    from_qty = int(from_row["qty"])
    new_from_qty = from_qty - qty
    if new_from_qty < 0:
        conn.close()
        raise ValueError(f"이동 수량이 출발 재고보다 큽니다. (재고:{from_qty})")
    cur.execute(
        "UPDATE inventory SET item_name=?, brand=?, qty=?, note=?, updated_at=? WHERE id=?",
        (item_name, brand, new_from_qty, note, ts, from_row["id"]),
    )

    # add to destination
    to_row = _get_inventory_row(cur, to_location, item_code, lot, spec)
    if to_row:
        new_to_qty = int(to_row["qty"]) + qty
        cur.execute(
            "UPDATE inventory SET item_name=?, brand=?, qty=?, note=?, updated_at=? WHERE id=?",
            (item_name, brand, new_to_qty, note, ts, to_row["id"]),
        )
    else:
        cur.execute(
            "INSERT INTO inventory(location,item_code,item_name,lot,spec,brand,qty,note,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (to_location, item_code, item_name, lot, spec, brand, qty, note, ts),
        )

    cur.execute(
        "INSERT INTO history(ts,action,from_location,to_location,item_code,item_name,lot,spec,brand,qty,note) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (ts, "move", from_location, to_location, item_code, item_name, lot, spec, brand, qty, note),
    )
    conn.commit()
    conn.close()
