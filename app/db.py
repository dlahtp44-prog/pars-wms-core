import os
import sqlite3

# 기본: 프로젝트 루트(/app) 기준으로 wms.db 생성
DB_PATH = os.getenv("DB_PATH", "wms.db")


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # 재고 테이블
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
        비고 TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime')),
        UNIQUE(창고, 로케이션, 품번, LOT)
    )
    """)

    # 이력 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS 이력 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        일시 TEXT DEFAULT (datetime('now','localtime')),
        구분 TEXT NOT NULL,
        창고 TEXT NOT NULL,
        품번 TEXT NOT NULL,
        LOT TEXT NOT NULL,
        출발로케이션 TEXT DEFAULT '',
        도착로케이션 TEXT DEFAULT '',
        수량 INTEGER NOT NULL,
        비고 TEXT DEFAULT ''
    )
    """)

    # 조회 성능용 인덱스(선택)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_재고_검색 ON 재고(창고, 로케이션, 품번, LOT)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_이력_검색 ON 이력(일시, 구분, 창고, 품번, LOT)")

    conn.commit()
    conn.close()
