
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="PARS WMS CORE")

@app.get("/", response_class=HTMLResponse)
def home():
    return '''
    <h1>PARS WMS</h1>
    <ul>
      <li><a href="/inbound">입고</a></li>
      <li><a href="/outbound">출고</a></li>
      <li><a href="/transfer">이동</a></li>
      <li><a href="/qr">QR</a></li>
      <li><a href="/inventory">재고</a></li>
      <li><a href="/history">이력</a></li>
      <li><a href="/calendar">달력</a></li>
      <li><a href="/admin">관리자</a></li>
    </ul>
    '''
