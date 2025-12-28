export async function postJson(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  if (!res.ok) {
    // FastAPI error format: {"detail": "..."} or {"detail":[...]}
    const msg = (data && data.detail) ? JSON.stringify(data.detail) : JSON.stringify(data);
    throw new Error(msg);
  }
  return data;
}

export function parseQrText(txt) {
  // Accept JSON or key=value;key=value
  const s = (txt || "").trim();
  if (!s) return {};
  if (s.startsWith("{") && s.endsWith("}")) {
    try { return JSON.parse(s); } catch { return {}; }
  }
  const out = {};
  s.split(/[;,&\n]/).forEach(part => {
    const p = part.trim();
    if (!p) return;
    const m = p.split("=");
    if (m.length >= 2) out[m[0].trim()] = m.slice(1).join("=").trim();
  });
  return out;
}
