import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "wms.db")

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inbound (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        warehouse TEXT NOT NULL,
        location TEXT NOT NULL,
        product_code TEXT NOT NULL,
        product_name TEXT NOT NULL,
        lot TEXT NOT NULL,
        spec TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        memo TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,            -- INBOUND / OUTBOUND / MOVE
        ref_table TEXT NOT NULL,         -- inbound, outbound, move
        ref_id INTEGER NOT NULL,
        warehouse TEXT NOT NULL,
        location_from TEXT DEFAULT '',
        location_to TEXT DEFAULT '',
        product_code TEXT NOT NULL,
        lot TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        memo TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
