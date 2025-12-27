
import sqlite3
from typing import Iterable, Optional

DB_PATH = "wms.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _table_columns(cur, table: str) -> set[str]:
    cur.execute(f"PRAGMA table_info('{table}')")
    return {r[1] for r in cur.fetchall()}

def _ensure_column(cur, table: str, col: str, ddl: str):
    cols = _table_columns(cur, table)
    if col not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # 재고
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 재고(
        창고 TEXT,
        로케이션 TEXT,
        품번 TEXT,
        품명 TEXT,
        LOT TEXT,
        규격 TEXT,
        수량 INTEGER,
        비고 TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime')),
        UNIQUE(창고, 로케이션, 품번, LOT)
    )
    """)

    # 이력
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 이력(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        구분 TEXT,
        창고 TEXT,
        품번 TEXT,
        품명 TEXT,
        LOT TEXT,
        규격 TEXT,
        출발로케이션 TEXT,
        도착로케이션 TEXT,
        수량 INTEGER,
        비고 TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )
    """)

    # 달력(공용)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS calendar(
        date TEXT PRIMARY KEY,
        content TEXT
    )
    """)

    # ---- Migration for older DBs (if tables existed without columns) ----
    # 재고 추가 컬럼
    _ensure_column(cur, "재고", "비고", "비고 TEXT DEFAULT ''")
    _ensure_column(cur, "재고", "created_at", "created_at TEXT DEFAULT (datetime('now','localtime'))")
    _ensure_column(cur, "재고", "updated_at", "updated_at TEXT DEFAULT (datetime('now','localtime'))")
    # 이력 비고 추가
    _ensure_column(cur, "이력", "비고", "비고 TEXT DEFAULT ''")

    conn.commit()
    conn.close()
