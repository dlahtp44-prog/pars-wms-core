window.addEventListener("load", loadReport);

async function loadReport() {
  const start = document.getElementById("start").value.trim();
  const end = document.getElementById("end").value.trim();

  const qs = new URLSearchParams();
  if (start) qs.set("start", start);
  if (end) qs.set("end", end);

  const res = await fetch("/api/report?" + qs.toString());
  const data = await res.json();

  const tbody = document.querySelector("#rep tbody");
  tbody.innerHTML = "";

  const actionMap = { INBOUND: "입고", OUTBOUND: "출고", MOVE: "이동" };

  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${actionMap[row.action] || row.action}</td>
      <td>${row.item_code || ""}</td>
      <td>${row.location_from || ""}</td>
      <td>${row.location_to || ""}</td>
      <td>${row.lot || ""}</td>
      <td style="text-align:right;">${row.quantity || 0}</td>
      <td>${(row.created_at || "").replace("T"," ")}</td>
    `;
    tbody.appendChild(tr);
  });
}

window.loadReport = loadReport;

window.downloadCSV = function () {
  const start = document.getElementById("start").value.trim();
  const end = document.getElementById("end").value.trim();
  const qs = new URLSearchParams();
  if (start) qs.set("start", start);
  if (end) qs.set("end", end);
  qs.set("fmt", "csv");
  window.location.href = "/api/report?" + qs.toString();
};
