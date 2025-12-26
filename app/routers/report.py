import csv
import io
from fastapi import APIRouter, Response, Query
from app.db import get_conn

router = APIRouter(prefix="/api", tags=["report"])

@router.get("/report")
def api_report(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
    fmt: str = Query(default="json", description="json|csv"),
):
    where = []
    params = []

    if start:
        where.append("date(created_at) >= date(?)")
        params.append(start)
    if end:
        where.append("date(created_at) <= date(?)")
        params.append(end)

    sql = """SELECT action, item_code, item_name, location_from, location_to, lot, quantity, created_at
             FROM history"""
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC"

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    data = [dict(r) for r in rows]

    if fmt.lower() == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(data[0].keys()) if data else
                                ["action","item_code","item_name","location_from","location_to","lot","quantity","created_at"])
        writer.writeheader()
        for r in data:
            writer.writerow(r)
        csv_bytes = output.getvalue().encode("utf-8-sig")
        return Response(content=csv_bytes, media_type="text/csv",
                        headers={"Content-Disposition": "attachment; filename=pars_wms_report.csv"})
    return data
