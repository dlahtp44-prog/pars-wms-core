window.addEventListener("load", loadHistory);

async function loadHistory() {
  const res = await fetch("/api/history");
  const data = await res.json();

  const tbody = document.querySelector("#his tbody");
  tbody.innerHTML = "";

  const actionMap = { INBOUND: "입고", OUTBOUND: "출고", MOVE: "이동" };

  data.forEach(row => {
    const tr = document.createElement("tr");
    const action = actionMap[row.action] || row.action;
    tr.innerHTML = `
      <td>${action}</td>
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
