
import sqlite3

DB_PATH = "wms.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Inventory (재고)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 재고(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        창고 TEXT NOT NULL,
        로케이션 TEXT NOT NULL,
        품번 TEXT NOT NULL,
        품명 TEXT NOT NULL,
        LOT TEXT NOT NULL,
        규격 TEXT NOT NULL,
        수량 INTEGER NOT NULL DEFAULT 0,
        비고 TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime')),
        UNIQUE(창고, 로케이션, 품번, LOT)
    )
    """)

    # History (이력)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 이력(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        구분 TEXT NOT NULL,
        창고 TEXT NOT NULL,
        품번 TEXT NOT NULL,
        LOT TEXT NOT NULL,
        출발로케이션 TEXT DEFAULT '',
        도착로케이션 TEXT DEFAULT '',
        수량 INTEGER NOT NULL,
        비고 TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )
    """)

    # Calendar (공용달력)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 공용달력(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        날짜 TEXT NOT NULL,
        제목 TEXT NOT NULL,
        내용 TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )
    """)

    conn.commit()
    conn.close()
