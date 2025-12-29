
ROOT 404 FIX (One-shot)

증상
- GET / -> 404 Not Found

원인
- 실행 중인 main.py에 GET / 라우트가 없음
- ZIP 내부에 main.py가 여러 개 있어 배포 시 잘못된 파일이 실행됨

해결
1) 이 ZIP의 app/main.py 하나만 '정본'으로 사용
2) GET / 를 /page/inbound 로 리다이렉트
3) pages + routers 를 명시적으로 include

적용 방법 (Railway)
- Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8080
- 기존 루트의 main.py / 중복 main.py 사용 중단
- 이 ZIP의 app/main.py 로 교체

정상 기준
- / 접속 시 입고 페이지로 이동
- /page/inbound 정상
- /page/inventory 정상
- /page/history 정상
