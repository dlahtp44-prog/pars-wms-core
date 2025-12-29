
422 오류 원인
- 기존 /api/inbound 는 JSON body(item)를 요구
- 화면(form)에서는 application/x-www-form-urlencoded 전송
- 필수 필드 mismatch로 422 발생

수정 내용
- /api/inbound 를 Form 기반으로 통일
- inbound / inventory / history 필드명 완전 통일
- 엑셀/수기 동일 로직 적용

적용
- app/routers/inbound.py 교체
- 서버 재시작
