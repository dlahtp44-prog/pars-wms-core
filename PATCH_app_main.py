
# app/main.py 에 추가

from app.pages import label_product, label_location
from app.routers import label

app.include_router(label_product.router)
app.include_router(label_location.router)
app.include_router(label.router)
