let qr = null;
let scanning = false;

function ensure() {
  if (!qr) qr = new Html5Qrcode("reader");
}

window.startScan = async function () {
  ensure();
  if (scanning) return;
  scanning = true;

  try {
    await qr.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: 220 },
      (decodedText) => {
        document.getElementById("location_input").value = decodedText.trim();
        lookup();
      }
    );
  } catch (e) {
    scanning = false;
    alert("카메라 시작 실패: " + e);
  }
};

window.stopScan = async function () {
  if (!qr || !scanning) return;
  await qr.stop();
  scanning = false;
};

window.lookup = async function () {
  const loc = document.getElementById("location_input").value.trim();
  document.getElementById("selected").innerText = loc || "-";
  if (!loc) return;

  const res = await fetch("/api/inventory/by-location/" + encodeURIComponent(loc));
  const data = await res.json();

  const tbody = document.querySelector("#locInv tbody");
  tbody.innerHTML = "";
  data.forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.item_code || ""}</td>
      <td>${r.item_name || ""}</td>
      <td>${r.brand || ""}</td>
      <td>${r.spec || ""}</td>
      <td>${r.lot || ""}</td>
      <td style="text-align:right;">${r.quantity || 0}</td>
    `;
    tbody.appendChild(tr);
  });
};
