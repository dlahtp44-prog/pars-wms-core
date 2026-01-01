import { postJson, parseQrText } from "./_util.js";

let qLoc=null, qItem=null;

function ensure() {
  if (!qLoc) qLoc = new Html5Qrcode("readerLoc");
  if (!qItem) qItem = new Html5Qrcode("readerItem");
}

async function startScanner(qr, onText) {
  await qr.start(
    { facingMode: "environment" },
    { fps: 10, qrbox: 220 },
    (decodedText) => onText(decodedText)
  );
}

window.startLoc = async function() {
  ensure();
  try {
    await startScanner(qLoc, (t)=> {
      document.getElementById("location").value = t.trim();
    });
  } catch(e){ alert("로케이션 카메라 실패: " + e); }
};

window.startItem = async function() {
  ensure();
  try {
    await startScanner(qItem, (t)=> {
      const obj = parseQrText(t);
      if (obj.item_code) document.getElementById("item_code").value = obj.item_code;
      if (obj.item_name) document.getElementById("item_name").value = obj.item_name;
      if (obj.lot) document.getElementById("lot").value = obj.lot;
    });
  } catch(e){ alert("제품 카메라 실패: " + e); }
};

window.stopAll = async function() {
  for (const q of [qLoc,qItem]) {
    if (!q) continue;
    try { await q.stop(); } catch {}
  }
};

window.submitOutbound = async function() {
  const payload = {
    item_code: document.getElementById("item_code").value.trim(),
    item_name: document.getElementById("item_name").value.trim() || null,
    lot: document.getElementById("lot").value.trim(),
    quantity: Number(document.getElementById("quantity").value || 0),
    location: document.getElementById("location").value.trim() || null,
    remark: document.getElementById("remark").value.trim() || null,
  };
  try {
    const data = await postJson("/api/outbound", payload);
    document.getElementById("result").textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById("result").textContent = "ERROR: " + e.message;
  }
};
