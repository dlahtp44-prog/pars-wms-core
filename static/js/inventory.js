window.addEventListener("load", loadInventory);

async function loadInventory() {
  const res = await fetch("/api/inventory");
  const data = await res.json();
  const tbody = document.querySelector("#inv tbody");
  tbody.innerHTML = "";
  data.forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.item_code || ""}</td>
      <td>${r.item_name || ""}</td>
      <td>${r.brand || ""}</td>
      <td>${r.spec || ""}</td>
      <td>${r.location || ""}</td>
      <td>${r.lot || ""}</td>
      <td style="text-align:right;">${r.quantity || 0}</td>
    `;
    tbody.appendChild(tr);
  });
}
