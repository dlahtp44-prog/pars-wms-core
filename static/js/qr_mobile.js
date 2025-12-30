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

  // 상태머신
  // mode:
  //  - "scan_any": 아무 QR이나 스캔
  //  - "select_items": (로케이션 스캔 후) 재고 선택
  //  - "scan_dst": 선택 완료 후 도착 로케이션 스캔
  //  - "scan_src_for_item": (상품 QR 직접 스캔 후) 출발 로케이션 스캔
  //  - "scan_dst_for_item": 출발 이후 도착 로케이션 스캔
  let mode = "scan_any";
  let ctx = {
    srcLocation: "",
    dstLocation: "",
    selected: [], // {item_code,item_name,lot,spec,brand,qty,note}
    itemFromQR: null, // {item_code,item_name,lot,spec,brand}
  };

  function setStatus(text, type="pill") {
    statusEl.textContent = text;
    statusEl.className = "pill" + (type ? " " + type : "");
  }

  function showRaw(text) {
    rawEl.textContent = text || "-";
  }

  function clearResult() {
    resultEl.innerHTML = "";
  }

  function escapeHtml(s) {
    return (s ?? "").toString()
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  // ---- QR 파싱 ----
  function looksLikeLocation(s) {
    // 예: B01-01-02-A
    return /^[A-Z]\d{2}-\d{2}-\d{2}-[A-Z]\d?$/i.test(s.trim());
  }

  function parseKVText(raw) {
    // 지원:
    // - "품번:766109/품명:XXX/LOT:E465/규격:..."
    // - "품번=766109|품명=XXX|LOT=E465|규격=..."
    // - "ITEM|품번=...|품명=...|LOT=...|규격=..."
    const cleaned = raw.replace(/^ITEM\|/i, "");
    const parts = cleaned.split(/[\/|]/).map(x => x.trim()).filter(Boolean);
    const obj = {};
    for (const p of parts) {
      const m = p.match(/^([^:=]+)\s*[:=]\s*(.+)$/);
      if (!m) continue;
      const key = m[1].trim();
      const val = m[2].trim();
      obj[key] = val;
    }
    // normalize keys
    const item_code = obj["품번"] || obj["item_code"] || obj["ITEM"] || obj["code"];
    const item_name = obj["품명"] || obj["item_name"] || obj["name"];
    const lot = obj["LOT"] || obj["Lot"] || obj["lot"];
    const spec = obj["규격"] || obj["spec"];
    const brand = obj["브랜드"] || obj["brand"] || "";
    return { item_code, item_name, lot, spec, brand };
  }

  function parseQR(raw) {
    const txt = (raw || "").trim();
    if (!txt) return { type: "unknown", raw: txt };

    // 1) 명시 prefix
    if (/^LOC\|/i.test(txt)) {
      const loc = txt.split("|")[1]?.trim() || "";
      return { type: "location", location: loc, raw: txt };
    }
    if (/^ITEM\|/i.test(txt)) {
      const item = parseKVText(txt);
      if (item.item_code && item.lot && item.spec) return { type: "item", item, raw: txt };
      return { type: "unknown", raw: txt };
    }

    // 2) 로케이션 패턴
    if (looksLikeLocation(txt)) {
      return { type: "location", location: txt, raw: txt };
    }

    // 3) 상품 패턴(키-값)
    const item = parseKVText(txt);
    if (item.item_code && item.lot && item.spec) {
      return { type: "item", item, raw: txt };
    }

    return { type: "unknown", raw: txt };
  }

  // ---- 카메라/스캐너 ----
  async function startCamera() {
    if (stream) return;
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } },
      audio: false
    });
    video.srcObject = stream;
    await video.play();
  }

  function stopCamera() {
    if (stream) {
      for (const t of stream.getTracks()) t.stop();
    }
    stream = null;
    video.srcObject = null;
  }

  function ensureDetector() {
    // Chrome/Edge 모바일 대부분 지원 (BarcodeDetector)
    if ("BarcodeDetector" in window) {
      detector = new window.BarcodeDetector({ formats: ["qr_code"] });
      return true;
    }
    return false;
  }

  async function scanLoop() {
    if (!running) return;

    const w = video.videoWidth || 0;
    const h = video.videoHeight || 0;
    if (!w || !h) {
      rafId = requestAnimationFrame(scanLoop);
      return;
    }

    canvas.width = w;
    canvas.height = h;
    const ctx2d = canvas.getContext("2d", { willReadFrequently: true });
    ctx2d.drawImage(video, 0, 0, w, h);

    try {
      const barcodes = await detector.detect(canvas);
      if (barcodes && barcodes.length) {
        const raw = barcodes[0].rawValue || "";
        await onDetected(raw);
      }
    } catch (e) {
      // ignore transient errors
    }

    rafId = requestAnimationFrame(scanLoop);
  }

  async function startScan() {
    clearResult();
    setStatus("카메라 실행중…");
    hintEl.textContent = "QR을 카메라 중앙에 맞추세요.";
    await startCamera();

    if (!ensureDetector()) {
      setStatus("이 브라우저는 QR 디텍터 미지원", "err");
      hintEl.textContent = "Chrome/Edge 모바일로 접속해 주세요.";
      return;
    }

    running = true;
    setStatus("스캔중", "ok");
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(scanLoop);
  }

  function stopScan() {
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
    setStatus("중지됨");
    hintEl.textContent = "스캔 시작을 누르면 재개됩니다.";
  }

  function resetAll() {
    stopScan();
    showRaw("-");
    clearResult();
    mode = "scan_any";
    ctx = { srcLocation:"", dstLocation:"", selected:[], itemFromQR:null };
    setStatus("초기화됨");
    hintEl.textContent = "로케이션 QR 또는 상품 QR을 스캔하세요.";
  }

  // ---- 렌더링 ----
  function renderInventorySelect(location, items) {
    clearResult();
    const rows = items || [];
    const html = `
      <div class="row" style="justify-content:space-between;">
        <div><b>로케이션:</b> <span class="pill">${escapeHtml(location)}</span></div>
        <div class="muted">총 ${rows.length}건</div>
      </div>
      <div style="height:8px"></div>
      <div class="muted">이동할 항목을 체크하고 수량을 입력 후 "선택 완료"를 누르세요.</div>
      <div style="height:10px"></div>
      <table>
        <thead>
          <tr>
            <th></th>
            <th>품번</th>
            <th>품명</th>
            <th>LOT</th>
            <th>규격</th>
            <th>재고</th>
            <th>이동수량</th>
          </tr>
        </thead>
        <tbody>
          ${rows.map((r, idx) => `
            <tr>
              <td><input type="checkbox" data-idx="${idx}" class="chk"/></td>
              <td>${escapeHtml(r.item_code ?? "")}</td>
              <td>${escapeHtml(r.item_name ?? "")}</td>
              <td>${escapeHtml(r.lot ?? "")}</td>
              <td>${escapeHtml(r.spec ?? "")}</td>
              <td>${escapeHtml(r.qty ?? "")}</td>
              <td><input type="number" min="1" max="${escapeHtml(r.qty ?? 999999)}" value="1" class="qty" data-idx="${idx}" style="width:92px"/></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
      <div style="height:10px"></div>
      <div class="row">
        <button id="btnConfirmSelect" type="button">선택 완료 → 도착 로케이션 스캔</button>
        <button id="btnBack" type="button" class="secondary">뒤로</button>
      </div>
    `;
    resultEl.innerHTML = html;

    $("btnBack").onclick = () => {
      mode = "scan_any";
      ctx.srcLocation = "";
      ctx.selected = [];
      clearResult();
      hintEl.textContent = "로케이션 QR 또는 상품 QR을 스캔하세요.";
    };

    $("btnConfirmSelect").onclick = () => {
      const chks = Array.from(document.querySelectorAll(".chk"));
      const qtyInputs = Array.from(document.querySelectorAll(".qty"));
      const selected = [];
      chks.forEach(chk => {
        if (!chk.checked) return;
        const idx = parseInt(chk.dataset.idx, 10);
        const q = qtyInputs.find(x => parseInt(x.dataset.idx, 10) === idx);
        const qty = Math.max(1, parseInt(q?.value || "1", 10));
        const r = rows[idx];
        selected.push({
          item_code: r.item_code,
          item_name: r.item_name,
          lot: r.lot,
          spec: r.spec,
          brand: r.brand || "",
          qty,
          note: "QR 이동"
        });
      });

      if (!selected.length) {
        alert("이동할 항목을 1개 이상 선택하세요.");
        return;
      }

      ctx.selected = selected;
      mode = "scan_dst";
      clearResult();
      resultEl.innerHTML = `
        <div class="muted">선택 완료 ✅ 이제 <b>도착 로케이션 QR</b>을 스캔하세요.</div>
        <div style="height:8px"></div>
        <div><b>출발:</b> <span class="pill">${escapeHtml(ctx.srcLocation)}</span></div>
        <div><b>선택:</b> <span class="pill">${selected.length}건</span></div>
      `;
      hintEl.textContent = "도착 로케이션 QR을 스캔하면 이동 API를 호출합니다.";
    };
  }

  function renderItemMoveFlow(item) {
    clearResult();
    const html = `
      <div><b>상품 QR 확인</b></div>
      <div style="height:8px"></div>
      <div class="row">
        <span class="pill">품번 ${escapeHtml(item.item_code || "")}</span>
        <span class="pill">LOT ${escapeHtml(item.lot || "")}</span>
        <span class="pill">규격 ${escapeHtml(item.spec || "")}</span>
      </div>
      <div style="height:10px"></div>
      <div class="row">
        <label class="muted">이동수량</label>
        <input id="singleQty" type="number" min="1" value="1" style="width:120px"/>
      </div>
      <div style="height:10px"></div>
      <div class="muted">이제 <b>출발 로케이션 QR</b>을 스캔하세요.</div>
    `;
    resultEl.innerHTML = html;
  }

  function renderDone(okCount, failCount, errors=[]) {
    clearResult();
    const html = `
      <div><b>이동 처리 완료</b></div>
      <div style="height:8px"></div>
      <div class="row">
        <span class="pill">성공 ${okCount}</span>
        <span class="pill">실패 ${failCount}</span>
      </div>
      ${errors.length ? `<div style="height:10px"></div><div class="muted">${errors.map(e=>escapeHtml(e)).join("<br/>")}</div>` : ""}
      <div style="height:10px"></div>
      <div class="row">
        <button id="btnNew" type="button">새로 스캔</button>
      </div>
    `;
    resultEl.innerHTML = html;
    $("btnNew").onclick = resetAll;
  }

  // ---- API 호출 ----
  async function fetchInventory(location) {
    const res = await fetch(`/api/qr/inventory?location=${encodeURIComponent(location)}`);
    if (!res.ok) throw new Error("재고 조회 실패");
    return await res.json();
  }

  async function callMove(fromLoc, toLoc, item) {
    const fd = new FormData();
    fd.append("from_location", fromLoc);
    fd.append("to_location", toLoc);
    fd.append("item_code", item.item_code);
    fd.append("item_name", item.item_name || "");
    fd.append("lot", item.lot || "");
    fd.append("spec", item.spec || "");
    fd.append("brand", item.brand || "");
    fd.append("qty", String(item.qty || 1));
    fd.append("note", item.note || "");
    const res = await fetch("/api/move", { method: "POST", body: fd });
    const j = await res.json().catch(()=> ({}));
    if (!res.ok || !j.ok) {
      throw new Error(j.detail || "이동 API 실패");
    }
    return j;
  }

  // ---- 스캔 결과 처리 ----
  async function onDetected(raw) {
    // 중복 인식 방지: 한번 감지되면 잠깐 멈춤
    stopScan();
    setStatus("인식됨", "ok");
    showRaw(raw);

    const p = parseQR(raw);

    if (mode === "scan_any") {
      if (p.type === "location") {
        ctx.srcLocation = p.location;
        mode = "select_items";
        hintEl.textContent = "재고를 불러오는 중…";
        try {
          const data = await fetchInventory(ctx.srcLocation);
          renderInventorySelect(ctx.srcLocation, data.items || []);
          hintEl.textContent = "이동할 항목을 선택 후 '선택 완료'를 누르세요.";
        } catch (e) {
          resultEl.innerHTML = `<div class="err">재고 조회 실패</div><div class="muted">${escapeHtml(e.message)}</div>`;
          mode = "scan_any";
        }
        return;
      }

      if (p.type === "item") {
        ctx.itemFromQR = p.item;
        mode = "scan_src_for_item";
        hintEl.textContent = "출발 로케이션 QR을 스캔하세요.";
        renderItemMoveFlow(p.item);
        return;
      }

      resultEl.innerHTML = `<div class="err">알 수 없는 QR</div><div class="muted">LOC|로케이션 또는 품번/LOT/규격 포함 QR만 지원합니다.</div>`;
      mode = "scan_any";
      return;
    }

    // 로케이션에서 재고 선택 완료 후 도착 스캔
    if (mode === "scan_dst") {
      if (p.type !== "location") {
        resultEl.innerHTML = `<div class="err">도착 로케이션 QR을 스캔하세요.</div>`;
        mode = "scan_dst";
        return;
      }
      ctx.dstLocation = p.location;

      hintEl.textContent = "이동 처리중…";
      setStatus("이동 처리중…");
      let ok = 0, fail = 0;
      const errors = [];
      for (const item of ctx.selected) {
        try {
          await callMove(ctx.srcLocation, ctx.dstLocation, item);
          ok++;
        } catch (e) {
          fail++;
          errors.push(`${item.item_code}/${item.lot}: ${e.message}`);
        }
      }
      setStatus("완료", "ok");
      renderDone(ok, fail, errors);
      mode = "scan_any";
      return;
    }

    // 상품 QR 직접 스캔 후 출발 로케이션 스캔
    if (mode === "scan_src_for_item") {
      if (p.type !== "location") {
        resultEl.innerHTML += `<div style="height:8px"></div><div class="err">출발 로케이션 QR을 스캔하세요.</div>`;
        mode = "scan_src_for_item";
        return;
      }
      ctx.srcLocation = p.location;
      mode = "scan_dst_for_item";
      hintEl.textContent = "도착 로케이션 QR을 스캔하세요.";
      resultEl.innerHTML += `<div style="height:8px"></div><div class="muted">출발 로케이션: <span class="pill">${escapeHtml(ctx.srcLocation)}</span></div>`;
      return;
    }

    // 상품 QR → 출발 → 도착
    if (mode === "scan_dst_for_item") {
      if (p.type !== "location") {
        resultEl.innerHTML += `<div style="height:8px"></div><div class="err">도착 로케이션 QR을 스캔하세요.</div>`;
        mode = "scan_dst_for_item";
        return;
      }
      ctx.dstLocation = p.location;

      const qtyInput = document.getElementById("singleQty");
      const qty = Math.max(1, parseInt(qtyInput?.value || "1", 10));
      const item = {
        ...(ctx.itemFromQR || {}),
        qty,
        note: "QR 이동"
      };

      hintEl.textContent = "이동 처리중…";
      setStatus("이동 처리중…");
      try {
        await callMove(ctx.srcLocation, ctx.dstLocation, item);
        setStatus("완료", "ok");
        renderDone(1, 0, []);
      } catch (e) {
        setStatus("실패", "err");
        renderDone(0, 1, [e.message]);
      }
      mode = "scan_any";
      return;
    }
  }

  // ---- 버튼 이벤트 ----
  btnStart?.addEventListener("click", async () => {
    try {
      await startScan();
    } catch (e) {
      setStatus("카메라 권한 필요", "err");
      hintEl.textContent = "브라우저에서 카메라 권한을 허용해 주세요.";
    }
  });

  btnStop?.addEventListener("click", () => stopScan());
  btnReset?.addEventListener("click", () => resetAll());

  // 초기 안내
  setStatus("대기중");
  hintEl.textContent = "스캔 시작을 누른 뒤 로케이션/상품 QR을 스캔하세요.";
})();
