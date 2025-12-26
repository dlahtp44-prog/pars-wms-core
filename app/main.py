
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.pages.home import router as home_router
from app.routers.inbound import router as inbound_router
from app.routers.inventory import router as inventory_router

app = FastAPI(title="PARS WMS CORE STABLE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(home_router)
app.include_router(inbound_router)
app.include_router(inventory_router)
