# app/db.py
import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

DB_PATH = os.environ.get("WMS_DB_PATH", "WMS.db")

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db() -> None:
    with get_conn() as conn:
        cur = conn.cursor()

        # Items master (품목 기본정보)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_code   TEXT PRIMARY KEY,
            item_name   TEXT,
            brand       TEXT,
            spec        TEXT,
            created_at  TEXT DEFAULT (datetime('now','localtime'))
        )
        """)

        # Inventory (재고: 로케이션/LOT 단위)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code   TEXT NOT NULL,
            item_name   TEXT,
            brand       TEXT,
            spec        TEXT,
            location    TEXT NOT NULL,
            lot         TEXT NOT NULL,
            quantity    INTEGER NOT NULL DEFAULT 0,
            updated_at  TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(item_code, location, lot)
        )
        """)

        # History (작업 이력)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            action        TEXT NOT NULL, -- INBOUND/OUTBOUND/MOVE
            item_code      TEXT NOT NULL,
            item_name      TEXT,
            lot            TEXT,
            quantity       INTEGER NOT NULL,
            location_from  TEXT,
            location_to    TEXT,
            remark         TEXT,
            created_at     TEXT DEFAULT (datetime('now','localtime'))
        )
        """)

# ---------------------------
# Helpers
# ---------------------------
def upsert_item(item_code: str, item_name: str|None, brand: str|None, spec: str|None) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO items(item_code,item_name,brand,spec)
            VALUES(?,?,?,?)
            ON CONFLICT(item_code) DO UPDATE SET
                item_name=excluded.item_name,
                brand=excluded.brand,
                spec=excluded.spec
            """,
            (item_code, item_name, brand, spec),
        )

def add_inventory(item_code: str, location: str, lot: str, quantity: int,
                  item_name: str|None=None, brand: str|None=None, spec: str|None=None) -> None:
    """재고 증가 (입고/이동 도착)"""
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO inventory(item_code,item_name,brand,spec,location,lot,quantity)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(item_code, location, lot) DO UPDATE SET
                quantity = inventory.quantity + excluded.quantity,
                item_name = COALESCE(excluded.item_name, inventory.item_name),
                brand = COALESCE(excluded.brand, inventory.brand),
                spec = COALESCE(excluded.spec, inventory.spec),
                updated_at = datetime('now','localtime')
            """,
            (item_code, item_name, brand, spec, location, lot, int(quantity)),
        )

def subtract_inventory_any_location(item_code: str, lot: str, quantity: int, prefer_location: str|None=None):
    """로케이션 지정이 없을 때도 출고 가능하게: 여러 로케이션에서 나눠 차감.
    반환: [(location, taken_qty), ...]
    """
    qty_left = int(quantity)
    taken = []

    with get_conn() as conn:
        cur = conn.cursor()
        if prefer_location:
            cur.execute(
                """SELECT location, quantity FROM inventory
                WHERE item_code=? AND lot=? AND location=? AND quantity>0""",
                (item_code, lot, prefer_location),
            )
            row = cur.fetchone()
            if row:
                take = min(qty_left, int(row["quantity"]))
                if take > 0:
                    conn.execute(
                        """UPDATE inventory SET quantity=quantity-?, updated_at=datetime('now','localtime')
                        WHERE item_code=? AND lot=? AND location=?""",
                        (take, item_code, lot, prefer_location),
                    )
                    taken.append((prefer_location, take))
                    qty_left -= take

        # 나머지는 다른 로케이션에서 차감
        if qty_left > 0:
            cur.execute(
                """SELECT location, quantity FROM inventory
                WHERE item_code=? AND lot=? AND quantity>0
                ORDER BY quantity DESC""",
                (item_code, lot),
            )
            rows = cur.fetchall()
            for r in rows:
                if qty_left <= 0:
                    break
                loc = r["location"]
                # prefer_location은 위에서 처리했으니 스킵
                if prefer_location and loc == prefer_location:
                    continue
                have = int(r["quantity"])
                take = min(qty_left, have)
                if take <= 0:
                    continue
                conn.execute(
                    """UPDATE inventory SET quantity=quantity-?, updated_at=datetime('now','localtime')
                    WHERE item_code=? AND lot=? AND location=?""",
                    (take, item_code, lot, loc),
                )
                taken.append((loc, take))
                qty_left -= take

        # 부족하면 롤백 유도(예외)
        if qty_left > 0:
            raise ValueError("출고 수량이 재고보다 많습니다.")

    return taken

def subtract_inventory_exact(item_code: str, location: str, lot: str, quantity: int) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT quantity FROM inventory WHERE item_code=? AND location=? AND lot=?""",
            (item_code, location, lot),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("재고가 존재하지 않습니다.")
        if int(row["quantity"]) < int(quantity):
            raise ValueError("출고/이동 수량이 재고보다 많습니다.")
        conn.execute(
            """UPDATE inventory
            SET quantity=quantity-?, updated_at=datetime('now','localtime')
            WHERE item_code=? AND location=? AND lot=?""",
            (int(quantity), item_code, location, lot),
        )

def insert_history(action: str, item_code: str, item_name: str|None, lot: str|None,
                   quantity: int, location_from: str|None, location_to: str|None, remark: str|None):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO history(action,item_code,item_name,lot,quantity,location_from,location_to,remark)
            VALUES(?,?,?,?,?,?,?,?)""",
            (action, item_code, item_name, lot, int(quantity), location_from, location_to, remark),
        )
