(() => {
  const $ = (id) => document.getElementById(id);
  const statusEl = $("status");
  const rawEl = $("raw");
  const resultEl = $("result");
  const hintEl = $("hint");
  const video = $("camera");
  const canvas = $("frame");
  const btnStart = $("btnStart");
  const btnStop = $("btnStop");
  const btnReset = $("btnReset");

  let stream = null;
  let running = false;
  let detector = null;
  let rafId = null;

  let mode = "scan_any";
  let ctx = { srcLocation:"", dstLocation:"", selected:[], itemFromQR:null };

  const setStatus = (t, cls="") => {
    statusEl.textContent = t;
    statusEl.className = "pill" + (cls ? " " + cls : "");
  };
  const escapeHtml = (s) => (s ?? "").toString()
    .replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;")
    .replaceAll('"',"&quot;").replaceAll("'","&#039;");

  const looksLikeLocation = (s) => /^[A-Z]\d{2}-\d{2}-\d{2}-[A-Z]\d?$/i.test((s||"").trim());

  function parseKVText(raw){
    const cleaned = raw.replace(/^ITEM\|/i, "");
    const parts = cleaned.split(/[\/|]/).map(x=>x.trim()).filter(Boolean);
    const obj = {};
    for (const p of parts){
      const m = p.match(/^([^:=]+)\s*[:=]\s*(.+)$/);
      if(!m) continue;
      obj[m[1].trim()] = m[2].trim();
    }
    return {
      item_code: obj["품번"] || obj["item_code"] || obj["code"],
      item_name: obj["품명"] || obj["item_name"] || obj["name"] || "",
      lot: obj["LOT"] || obj["lot"] || "",
      spec: obj["규격"] || obj["spec"] || "",
      brand: obj["브랜드"] || obj["brand"] || ""
    };
  }

  function parseQR(raw){
    const txt = (raw||"").trim();
    if(!txt) return {type:"unknown", raw:txt};
    if(/^LOC\|/i.test(txt)) return {type:"location", location:(txt.split("|")[1]||"").trim(), raw:txt};
    if(/^ITEM\|/i.test(txt)){
      const item=parseKVText(txt);
      if(item.item_code && item.lot && item.spec) return {type:"item", item, raw:txt};
      return {type:"unknown", raw:txt};
    }
    if(looksLikeLocation(txt)) return {type:"location", location:txt, raw:txt};
    const item=parseKVText(txt);
    if(item.item_code && item.lot && item.spec) return {type:"item", item, raw:txt};
    return {type:"unknown", raw:txt};
  }

  async function startCamera(){
    if(stream) return;
    stream = await navigator.mediaDevices.getUserMedia({ video:{ facingMode:{ ideal:"environment"}}, audio:false });
    video.srcObject = stream;
    await video.play();
  }
  function stopCamera(){
    if(stream){ for(const t of stream.getTracks()) t.stop(); }
    stream=null; video.srcObject=null;
  }
  function ensureDetector(){
    if("BarcodeDetector" in window){
      detector = new window.BarcodeDetector({ formats:["qr_code"] });
      return true;
    }
    return false;
  }

  async function scanLoop(){
    if(!running) return;
    const w = video.videoWidth||0, h = video.videoHeight||0;
    if(!w||!h){ rafId=requestAnimationFrame(scanLoop); return; }
    canvas.width=w; canvas.height=h;
    const c2d = canvas.getContext("2d", { willReadFrequently:true });
    c2d.drawImage(video,0,0,w,h);
    try{
      const codes = await detector.detect(canvas);
      if(codes && codes.length){
        const raw = codes[0].rawValue || "";
        await onDetected(raw);
      }
    }catch(e){}
    rafId=requestAnimationFrame(scanLoop);
  }

  function stopScan(){
    running=false;
    if(rafId) cancelAnimationFrame(rafId);
    rafId=null;
    setStatus("중지됨");
  }

  function resetAll(){
    stopScan();
    rawEl.textContent="-";
    resultEl.innerHTML="";
    mode="scan_any";
    ctx={ srcLocation:"", dstLocation:"", selected:[], itemFromQR:null };
    setStatus("대기중");
    hintEl.textContent="스캔 시작을 누른 뒤 로케이션/상품 QR을 스캔하세요.";
  }

  async function startScan(){
    resultEl.innerHTML="";
    setStatus("카메라 실행중…");
    await startCamera();
    if(!ensureDetector()){
      setStatus("QR 디텍터 미지원", "err");
      hintEl.textContent="Chrome/Edge 모바일로 접속해 주세요.";
      return;
    }
    running=true;
    setStatus("스캔중", "ok");
    hintEl.textContent="QR을 카메라 중앙에 맞추세요.";
    if(rafId) cancelAnimationFrame(rafId);
    rafId=requestAnimationFrame(scanLoop);
  }

  async function fetchInventory(location){
    const res = await fetch(`/api/qr/inventory?location=${encodeURIComponent(location)}`);
    if(!res.ok) throw new Error("재고 조회 실패");
    return await res.json();
  }

  async function callMove(fromLoc, toLoc, item){
    const fd = new FormData();
    fd.append("from_location", fromLoc);
    fd.append("to_location", toLoc);
    fd.append("item_code", item.item_code);
    fd.append("item_name", item.item_name||"");
    fd.append("lot", item.lot||"");
    fd.append("spec", item.spec||"");
    fd.append("brand", item.brand||"");
    fd.append("qty", String(item.qty||1));
    fd.append("note", item.note||"QR 이동");
    const res = await fetch("/api/move", { method:"POST", body:fd });
    const j = await res.json().catch(()=>({}));
    if(!res.ok || !j.ok) throw new Error(j.detail || "이동 API 실패");
    return j;
  }

  function renderInventorySelect(location, items){
    const rows = items||[];
    resultEl.innerHTML = `
      <div class="muted">출발 로케이션: <span class="pill">${escapeHtml(location)}</span> / 총 ${rows.length}건</div>
      <div style="height:8px"></div>
      <div class="muted">이동할 항목 체크 후 수량 입력 → “선택 완료” → 도착 로케이션 스캔</div>
      <div style="height:10px"></div>
      <table>
        <thead><tr>
          <th></th><th>품번</th><th>품명</th><th>LOT</th><th>규격</th><th>재고</th><th>이동수량</th>
        </tr></thead>
        <tbody>
          ${rows.map((r, i)=>`
            <tr>
              <td><input type="checkbox" class="chk" data-idx="${i}"></td>
              <td>${escapeHtml(r.item_code||"")}</td>
              <td>${escapeHtml(r.item_name||"")}</td>
              <td>${escapeHtml(r.lot||"")}</td>
              <td>${escapeHtml(r.spec||"")}</td>
              <td>${escapeHtml(r.qty||"")}</td>
              <td><input type="number" class="qty" data-idx="${i}" min="1" value="1" style="width:92px"></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
      <div style="height:10px"></div>
      <div class="row">
        <button id="btnConfirm" type="button">선택 완료 → 도착 로케이션 스캔</button>
        <button id="btnBack" type="button" class="secondary">뒤로</button>
      </div>
    `;
    document.getElementById("btnBack").onclick = resetAll;
    document.getElementById("btnConfirm").onclick = () => {
      const selected=[];
      const chks=[...document.querySelectorAll(".chk")];
      const qtys=[...document.querySelectorAll(".qty")];
      chks.forEach(chk=>{
        if(!chk.checked) return;
        const idx=parseInt(chk.dataset.idx,10);
        const q=qtys.find(x=>parseInt(x.dataset.idx,10)===idx);
        const qty=Math.max(1, parseInt(q?.value||"1",10));
        const r=rows[idx];
        selected.push({ item_code:r.item_code, item_name:r.item_name, lot:r.lot, spec:r.spec, brand:r.brand||"", qty, note:"QR 이동" });
      });
      if(!selected.length){ alert("이동할 항목을 1개 이상 선택하세요."); return; }
      ctx.selected=selected;
      mode="scan_dst";
      resultEl.innerHTML = `<div class="muted">선택 완료 ✅ 이제 <b>도착 로케이션 QR</b>을 스캔하세요.</div>`;
      hintEl.textContent="도착 로케이션 QR을 스캔하면 이동 API를 호출합니다.";
    };
  }

  function renderItemMoveFlow(item){
    resultEl.innerHTML = `
      <div class="muted">상품 QR 확인</div>
      <div style="height:8px"></div>
      <div class="row">
        <span class="pill">품번 ${escapeHtml(item.item_code||"")}</span>
        <span class="pill">LOT ${escapeHtml(item.lot||"")}</span>
        <span class="pill">규격 ${escapeHtml(item.spec||"")}</span>
      </div>
      <div style="height:10px"></div>
      <div class="row"><span class="muted">이동수량</span>
        <input id="singleQty" type="number" min="1" value="1" style="width:120px"/>
      </div>
      <div style="height:10px"></div>
      <div class="muted">이제 <b>출발 로케이션 QR</b>을 스캔하세요.</div>
    `;
  }

  function renderDone(ok, fail, errors=[]){
    resultEl.innerHTML = `
      <div><b>이동 처리 완료</b></div>
      <div style="height:8px"></div>
      <div class="row"><span class="pill">성공 ${ok}</span><span class="pill">실패 ${fail}</span></div>
      ${errors.length ? `<div style="height:10px"></div><div class="muted">${errors.map(escapeHtml).join("<br/>")}</div>` : ""}
      <div style="height:10px"></div>
      <div class="row"><button id="btnNew" type="button">새로 스캔</button></div>
    `;
    document.getElementById("btnNew").onclick = resetAll;
  }

  async function onDetected(raw){
    stopScan(); // 중복 인식 방지
    rawEl.textContent = raw;
    const p = parseQR(raw);

    if(mode==="scan_any"){
      if(p.type==="location"){
        ctx.srcLocation = p.location;
        mode="select_items";
        hintEl.textContent="재고 불러오는 중…";
        try{
          const data = await fetchInventory(ctx.srcLocation);
          renderInventorySelect(ctx.srcLocation, data.items||[]);
          hintEl.textContent="이동할 항목 선택 후 '선택 완료'를 누르세요.";
        }catch(e){
          resultEl.innerHTML = `<div class="err">재고 조회 실패</div><div class="muted">${escapeHtml(e.message)}</div>`;
          mode="scan_any";
        }
        return;
      }
      if(p.type==="item"){
        ctx.itemFromQR=p.item;
        mode="scan_src_for_item";
        hintEl.textContent="출발 로케이션 QR을 스캔하세요.";
        renderItemMoveFlow(p.item);
        return;
      }
      resultEl.innerHTML = `<div class="err">알 수 없는 QR</div><div class="muted">로케이션 또는 품번/LOT/규격 포함 QR만 지원합니다.</div>`;
      mode="scan_any";
      return;
    }

    if(mode==="scan_dst"){
      if(p.type!=="location"){
        resultEl.innerHTML = `<div class="err">도착 로케이션 QR을 스캔하세요.</div>`;
        return;
      }
      ctx.dstLocation=p.location;
      setStatus("이동 처리중…");
      hintEl.textContent="이동 처리중…";
      let ok=0, fail=0;
      const errors=[];
      for(const item of ctx.selected){
        try{ await callMove(ctx.srcLocation, ctx.dstLocation, item); ok++; }
        catch(e){ fail++; errors.push(`${item.item_code}/${item.lot}: ${e.message}`); }
      }
      setStatus("완료","ok");
      renderDone(ok, fail, errors);
      mode="scan_any";
      return;
    }

    if(mode==="scan_src_for_item"){
      if(p.type!=="location"){
        resultEl.innerHTML += `<div style="height:8px"></div><div class="err">출발 로케이션 QR을 스캔하세요.</div>`;
        return;
      }
      ctx.srcLocation=p.location;
      mode="scan_dst_for_item";
      hintEl.textContent="도착 로케이션 QR을 스캔하세요.";
      resultEl.innerHTML += `<div style="height:8px"></div><div class="muted">출발: <span class="pill">${escapeHtml(ctx.srcLocation)}</span></div>`;
      return;
    }

    if(mode==="scan_dst_for_item"){
      if(p.type!=="location"){
        resultEl.innerHTML += `<div style="height:8px"></div><div class="err">도착 로케이션 QR을 스캔하세요.</div>`;
        return;
      }
      ctx.dstLocation=p.location;
      const qty = Math.max(1, parseInt(document.getElementById("singleQty")?.value || "1", 10));
      const item = { ...(ctx.itemFromQR||{}), qty, note:"QR 이동" };
      setStatus("이동 처리중…");
      try{
        await callMove(ctx.srcLocation, ctx.dstLocation, item);
        setStatus("완료","ok");
        renderDone(1,0,[]);
      }catch(e){
        setStatus("실패","err");
        renderDone(0,1,[e.message]);
      }
      mode="scan_any";
      return;
    }
  }

  btnStart?.addEventListener("click", async ()=>{
    try{ await startScan(); }
    catch(e){ setStatus("카메라 권한 필요","err"); hintEl.textContent="브라우저에서 카메라 권한을 허용해 주세요."; }
  });
  btnStop?.addEventListener("click", ()=>stopScan());
  btnReset?.addEventListener("click", ()=>resetAll());

  resetAll();
})();
