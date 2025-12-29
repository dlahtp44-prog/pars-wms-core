
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.db import get_db
import io
import csv

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("")
def history_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT 
        location,
        item_code,
        lot,
        spec,
        brand,
        qty,
        updated_at,
        memo,
        created_at
    FROM history
    ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    return [
        {
            "location": r[0],
            "item_code": r[1],
            "lot": r[2],
            "spec": r[3],
            "brand": r[4],
            "qty": r[5],
            "updated_at": r[6],
            "memo": r[7],
            "created_at": r[8],
        }
        for r in rows
    ]


@router.get("/excel")
def history_excel():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT 
        location,
        item_code,
        lot,
        spec,
        brand,
        qty,
        updated_at,
        memo,
        created_at
    FROM history
    ORDER BY created_at DESC
    """)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["로케이션","품번","LOT","규격","브랜드","수량","업데이트","비고","시간"]
    )

    for r in cur.fetchall():
        writer.writerow(r)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=history.csv"
        }
    )
