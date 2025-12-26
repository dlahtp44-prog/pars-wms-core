
import sqlite3
DB_PATH = "wms.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 재고(
        창고 TEXT, 로케이션 TEXT,
        품번 TEXT, 품명 TEXT,
        LOT TEXT, 규격 TEXT,
        수량 INTEGER,
        UNIQUE(창고, 로케이션, 품번, LOT)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 이력(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        구분 TEXT, 창고 TEXT,
        품번 TEXT, 품명 TEXT,
        LOT TEXT, 규격 TEXT,
        출발로케이션 TEXT,
        도착로케이션 TEXT,
        수량 INTEGER,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")
    conn.commit()
    conn.close()
