
# app/main.py 에 추가

from app.pages import print_inventory, print_history
from app.routers import print as print_router

app.include_router(print_inventory.router)
app.include_router(print_history.router)
app.include_router(print_router.router)
