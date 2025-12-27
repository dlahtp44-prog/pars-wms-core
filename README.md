
# PARS WMS CORE (Mobile/Tablet)

## Run locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## URLs
- Mobile menu: `/m`
- Inbound: `/입고`
- Outbound: `/출고`
- Move: `/이동`
- QR scan: `/m/qr`
- Inventory: `/재고`
- History: `/이력`
- Calendar: `/달력`
- Admin: `/관리자` (login required)

## Admin login
- `/login`
- Default password: `admin123` (set env `ADMIN_PASSWORD` to change)
