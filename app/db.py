import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "WMS.db")

def _dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = _dict_factory
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cur = conn.cursor()

        # Inbound / Outbound / Move
        cur.execute("""
        CREATE TABLE IF NOT EXISTS inbound (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            location TEXT NOT NULL,
            item_code TEXT NOT NULL,
            item_name TEXT NOT NULL,
            lot TEXT NOT NULL,
            spec TEXT NOT NULL,
            brand TEXT DEFAULT "",
            qty INTEGER NOT NULL,
            note TEXT DEFAULT ""
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS outbound (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            location TEXT NOT NULL,
            item_code TEXT NOT NULL,
            item_name TEXT NOT NULL,
            lot TEXT NOT NULL,
            spec TEXT NOT NULL,
            brand TEXT DEFAULT "",
            qty INTEGER NOT NULL,
            note TEXT DEFAULT ""
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            src_location TEXT NOT NULL,
            dst_location TEXT NOT NULL,
            item_code TEXT NOT NULL,
            item_name TEXT NOT NULL,
            lot TEXT NOT NULL,
            spec TEXT NOT NULL,
            brand TEXT DEFAULT "",
            qty INTEGER NOT NULL,
            note TEXT DEFAULT ""
        )
        """)

        # History (unified)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            kind TEXT NOT NULL,            -- inbound/outbound/move
            location TEXT NOT NULL,        -- for move: dst_location
            src_location TEXT DEFAULT "",  -- only move
            item_code TEXT NOT NULL,
            item_name TEXT NOT NULL,
            lot TEXT NOT NULL,
            spec TEXT NOT NULL,
            brand TEXT DEFAULT "",
            qty INTEGER NOT NULL,
            note TEXT DEFAULT ""
        )
        """)

        # Calendar memos
        cur.execute("""
        CREATE TABLE IF NOT EXISTS calendar_memo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ymd TEXT NOT NULL,       -- YYYY-MM-DD
            author TEXT DEFAULT "",
            memo TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_calendar_memo_ymd ON calendar_memo(ymd)")

def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
