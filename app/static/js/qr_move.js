import { postJson, parseQrText } from "./_util.js";

let qFrom=null, qItem=null, qTo=null;

function ensure() {
  if (!qFrom) qFrom = new Html5Qrcode("readerFrom");
  if (!qItem) qItem = new Html5Qrcode("readerItem");
  if (!qTo) qTo = new Html5Qrcode("readerTo");
}

async function startScanner(qr, onText) {
  await qr.start(
    { facingMode: "environment" },
    { fps: 10, qrbox: 220 },
    (decodedText) => onText(decodedText)
  );
}

window.startFrom = async function() {
  ensure();
  try {
    await startScanner(qFrom, (t)=> {
      document.getElementById("from_location").value = t.trim();
    });
  } catch(e){ alert("출발지 카메라 실패: " + e); }
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

window.startTo = async function() {
  ensure();
  try {
    await startScanner(qTo, (t)=> {
      document.getElementById("to_location").value = t.trim();
    });
  } catch(e){ alert("도착지 카메라 실패: " + e); }
};

window.stopAll = async function() {
  for (const q of [qFrom,qItem,qTo]) {
    if (!q) continue;
    try { await q.stop(); } catch {}
  }
};

window.submitMove = async function() {
  const payload = {
    item_code: document.getElementById("item_code").value.trim(),
    item_name: document.getElementById("item_name").value.trim() || null,
    lot: document.getElementById("lot").value.trim(),
    quantity: Number(document.getElementById("quantity").value || 0),
    from_location: document.getElementById("from_location").value.trim(),
    to_location: document.getElementById("to_location").value.trim(),
  };
  try {
    const data = await postJson("/api/move", payload);
    document.getElementById("result").textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById("result").textContent = "ERROR: " + e.message;
  }
};
