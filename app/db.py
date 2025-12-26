import os
import sqlite3

DB_NAME = os.getenv("WMS_DB", "wms.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    cur = conn.cursor()

    # 재고(표준 한글 컬럼)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 재고 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        창고 TEXT NOT NULL,
        로케이션 TEXT NOT NULL,
        품번 TEXT NOT NULL,
        품명 TEXT NOT NULL,
        LOT TEXT NOT NULL,
        규격 TEXT NOT NULL,
        수량 INTEGER NOT NULL DEFAULT 0,
        비고 TEXT DEFAULT ''
    );
    """)

    # 재고 유니크 키(창고+로케이션+품번+LOT) : 같은 키는 합산
    cur.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS ux_재고_키
    ON 재고(창고, 로케이션, 품번, LOT);
    """)

    # 이력(입고/출고/이동 + QR 포함)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 이력 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        일시 DATETIME DEFAULT CURRENT_TIMESTAMP,
        구분 TEXT NOT NULL,                 -- 입고 / 출고 / 이동
        창고 TEXT NOT NULL,
        품번 TEXT NOT NULL,
        LOT TEXT NOT NULL,
        출발로케이션 TEXT DEFAULT '',
        도착로케이션 TEXT DEFAULT '',
        수량 INTEGER NOT NULL,
        비고 TEXT DEFAULT ''
    );
    """)

    conn.commit()
    conn.close()
