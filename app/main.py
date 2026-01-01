
from fastapi import FastAPI, Depends, HTTPException
from app.routers import inbound, move, outbound, location
from app.admin import location_admin, summary_admin
from app.auth import get_current_user, admin_required
from app.db import init_db

app = FastAPI(title="PARS WMS v1.4 OPS")

init_db()

app.include_router(inbound.router)
app.include_router(move.router)
app.include_router(outbound.router)
app.include_router(location.router)

app.include_router(location_admin.router, dependencies=[Depends(admin_required)])
app.include_router(summary_admin.router, dependencies=[Depends(admin_required)])
