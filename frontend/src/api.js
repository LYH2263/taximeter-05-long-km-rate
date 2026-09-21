export async function getJSON(path) {
  const r = await fetch(path)
  if (!r.ok) throw new Error(await errText(r))
  return r.json()
}
export async function postJSON(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: body === undefined ? undefined : JSON.stringify(body) })
  if (!r.ok) throw new Error(await errText(r))
  return r.json()
}
export async function putJSON(path, body) {
  const r = await fetch(path, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await errText(r))
  return r.json()
}
async function errText(r) {
  const raw = await r.text()
  try { return JSON.parse(raw).detail ?? raw } catch { return raw }
}
