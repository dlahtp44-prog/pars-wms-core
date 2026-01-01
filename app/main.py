
from fastapi import FastAPI
from app.routers import inbound, move, location
from app.admin import location_admin

app = FastAPI(title="PARS WMS v1.3")

app.include_router(inbound.router)
app.include_router(move.router)
app.include_router(location.router)
app.include_router(location_admin.router)
