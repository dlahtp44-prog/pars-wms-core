from __future__ import annotations
import os
import sqlite3
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

DB_PATH = os.getenv("DB_PATH", "WMS.db")

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL,
        item_code TEXT NOT NULL,
        item_name TEXT NOT NULL,
        lot TEXT NOT NULL,
        spec TEXT NOT NULL,
        brand TEXT DEFAULT '',
        qty INTEGER NOT NULL DEFAULT 0,
        note TEXT DEFAULT '',
        updated_at TEXT NOT NULL
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_inventory_key ON inventory(location, item_code, lot, spec)")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        action TEXT NOT NULL,           -- inbound/outbound/move
        location TEXT DEFAULT '',
        from_location TEXT DEFAULT '',
        to_location TEXT DEFAULT '',
        item_code TEXT NOT NULL,
        item_name TEXT NOT NULL,
        lot TEXT NOT NULL,
        spec TEXT NOT NULL,
        brand TEXT DEFAULT '',
        qty INTEGER NOT NULL,
        note TEXT DEFAULT ''
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_history_ts ON history(ts)")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS calendar_memo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ymd TEXT NOT NULL,              -- YYYY-MM-DD
        author TEXT DEFAULT '',
        memo TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_calendar_ymd ON calendar_memo(ymd)")

    conn.commit()
    conn.close()

def now_kst_iso() -> str:
    return datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S")
