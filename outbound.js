import { postJson } from "./_util.js";

window.submitOutbound = async function () {
  const payload = {
    item_code: document.getElementById("item_code").value.trim(),
    item_name: document.getElementById("item_name").value.trim(),
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
