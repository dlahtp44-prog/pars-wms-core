import { postJson } from "./_util.js";

window.submitInbound = async function () {
  const payload = {
    item_code: document.getElementById("item_code").value.trim(),
    item_name: document.getElementById("item_name").value.trim(),
    brand: document.getElementById("brand").value.trim(),
    spec: document.getElementById("spec").value.trim(),
    location: document.getElementById("location").value.trim(),
    lot: document.getElementById("lot").value.trim(),
    quantity: Number(document.getElementById("quantity").value || 0),
  };
  try {
    const data = await postJson("/api/inbound", payload);
    document.getElementById("result").textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById("result").textContent = "ERROR: " + e.message;
  }
};
