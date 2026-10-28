export const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const K = { a: "sa_access", r: "sa_refresh" };
export const tokens = {
  access: () => (typeof window === "undefined" ? null : localStorage.getItem(K.a)),
  set: (a: string, r: string) => { localStorage.setItem(K.a, a); localStorage.setItem(K.r, r); },
  clear: () => { localStorage.removeItem(K.a); localStorage.removeItem(K.r); localStorage.removeItem("sa_user"); },
};

/** Refresh tokens and return the new session (incl. current organizations), or null. */
export async function refreshSession(): Promise<any | null> {
  const rt = localStorage.getItem(K.r);
  if (!rt) return null;
  const res = await fetch(`${BASE}/auth/refresh`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh_token: rt }) });
  if (!res.ok) return null;
  const d = await res.json();
  tokens.set(d.access_token, d.refresh_token);
  return d;
}

async function refresh(): Promise<boolean> {
  const rt = localStorage.getItem(K.r);
  if (!rt) return false;
  const res = await fetch(`${BASE}/auth/refresh`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh_token: rt }) });
  if (!res.ok) return false;
  const d = await res.json();
  tokens.set(d.access_token, d.refresh_token);
  return true;
}

function errMsg(d: any, fallback: string) {
  if (!d?.detail) return fallback;
  return typeof d.detail === "string" ? d.detail : d.detail.map((x: any) => x.msg).join(", ");
}

export async function api<T = any>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const t = tokens.access();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (res.status === 401 && retry && (await refresh())) return api<T>(path, init, false);
  if (res.status === 401) { tokens.clear(); if (typeof window !== "undefined" && !path.startsWith("/auth")) window.location.href = "/login"; }
  if (!res.ok) throw new Error(errMsg(await res.json().catch(() => null), `Request failed (${res.status})`));
  return res.status === 204 ? (undefined as T) : res.json();
}

type Handlers = { meta?: (d: any) => void; status?: (s: string) => void; token?: (t: string) => void; done?: () => void; error?: (m: string) => void };

/** POST /api/v1/chat/stream, parsing SSE: meta, status, token*, done | error */
export async function streamChat(message: string, conversation_id: string | null, organization_id: string | null, h: Handlers, retry = true) {
  const res = await fetch(`${BASE}/api/v1/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${tokens.access()}` },
    body: JSON.stringify({ message, conversation_id, organization_id }),
  });
  if (res.status === 401 && retry && (await refresh())) return streamChat(message, conversation_id, organization_id, h, false);
  if (!res.ok || !res.body) return h.error?.(errMsg(await res.json().catch(() => null), "Could not reach the assistant."));
  const reader = res.body.getReader(), dec = new TextDecoder();
  let buf = "";
  const parse = (raw: string) => { try { return JSON.parse(raw); } catch { return raw; } };
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const blocks = buf.split("\n\n");
    buf = blocks.pop() ?? "";
    for (const b of blocks) {
      let ev = "message"; const data: string[] = [];
      for (const line of b.split("\n")) {
        if (line.startsWith("event:")) ev = line.slice(6).trim();
        else if (line.startsWith("data:")) data.push(line.slice(5).replace(/^ /, ""));
      }
      const d = parse(data.join("\n"));
      const text = typeof d === "string" ? d : d?.text ?? d?.token ?? d?.message ?? "";
      if (ev === "meta") h.meta?.(d);
      else if (ev === "status") h.status?.(text);
      else if (ev === "token") h.token?.(typeof d === "string" ? data.join("\n") : text);
      else if (ev === "error") return h.error?.(text || "Something went wrong.");
      else if (ev === "done") return h.done?.();
    }
  }
  h.done?.();
}
