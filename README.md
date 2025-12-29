
REAL FIX v2

원인
- 이전 ZIP에서 Form(""") 잘못된 escape로 SyntaxError 발생

해결
- brand: str = Form("") 로 정상화
- 입고 시 inventory + history 모든 필드 저장
- history 엑셀 다운로드 포함

적용
- app/main.py 교체
- 서버 재시작
