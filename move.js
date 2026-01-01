import { postJson } from "./_util.js";

window.submitMove = async function () {
  const payload = {
    item_code: document.getElementById("item_code").value.trim(),
    item_name: document.getElementById("item_name").value.trim(),
    lot: document.getElementById("lot").value.trim(),
    quantity: Number(document.getElementById("quantity").value || 0),
    from_location: document.getElementById("from_location").value.trim(),
    to_location: document.getElementById("to_location").value.trim(),
    remark: document.getElementById("remark").value.trim() || null,
  };
  try {
    const data = await postJson("/api/move", payload);
    document.getElementById("result").textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById("result").textContent = "ERROR: " + e.message;
  }
};
