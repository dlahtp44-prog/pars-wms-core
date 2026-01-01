# PARS WMS (Core)

## Run locally
```bash
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## URLs
- PC 메인: /
- 모바일: /m
- 모바일 QR: /m/qr
- 관리자: /page/admin
