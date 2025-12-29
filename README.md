원샷 FIX 패키지 (422 + 404 한번에 해결)

현재 증상
- POST /api/inbound -> 422 (body.item missing)
- POST /api/inbound/excel -> 404 Not Found

원인
- inbound.html 수기입고 폼 필드명이 item_code 인데,
  서버 app/main.py 의 /api/inbound 는 item 을 필수로 요구해서 422 발생
- /api/inbound/excel 엔드포인트가 app/main.py 에 없어서 404 발생

해결
1) /api/inbound 가 item 또는 item_code 둘 다 받도록 수정
2) /api/inbound/excel 엔드포인트 추가 (openpyxl로 xlsx 처리)
3) requirements.txt 에 openpyxl 추가

적용 방법
- app/main.py 교체
- requirements.txt 교체
- Railway 재배포/재시작

정상 기준
- 수기 입고 저장 시 422 없어지고 /page/inbound로 돌아옴
- 엑셀 업로드 시 404 없어지고 /page/inbound로 돌아옴
- /page/inventory 에 재고 표시
- /page/history 에 이력 표시
