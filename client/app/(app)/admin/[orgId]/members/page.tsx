"use client";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { MailPlus, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button, Card, Empty, ErrorNote, Input, Spinner } from "@/components/ui";

type Member = { user_id: string; name?: string | null; email: string; role: string; status?: string };
const ROLES = [{ v: "member", l: "Member" }, { v: "admin", l: "Admin" }];

export default function Members() {
  const { orgId } = useParams<{ orgId: string }>();
  const { user } = useAuth();
  const [list, setList] = useState<Member[] | null>(null);
  const [f, setF] = useState({ email: "", role: "member" });
  const [err, setErr] = useState(""); const [note, setNote] = useState(""); const [busy, setBusy] = useState(false);
  const base = `/organizations/${orgId}/members`;

  const load = useCallback(() => api<any>(base).then((d) => setList((Array.isArray(d) ? d : d?.members ?? []).map((m: any) => ({ ...m, user_id: m.user_id ?? m.id })))).catch((e) => setErr(e.message)), [base]);
  useEffect(() => { load(); }, [load]);

  const act = async (fn: () => Promise<unknown>, ok?: string) => {
    setErr(""); setNote("");
    try { await fn(); if (ok) setNote(ok); await load(); } catch (x: any) { setErr(x.message); }
  };
  const invite = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true);
    await act(() => api(base, { method: "POST", body: JSON.stringify(f) }), `Invitation sent to ${f.email}.`);
    setF({ email: "", role: "member" }); setBusy(false);
  };
  const setRole = (m: Member, role: string) => act(() => api(`${base}/${m.user_id}`, { method: "PATCH", body: JSON.stringify({ role }) }), `${m.name ?? m.email} is now ${role}.`);
  const remove = (m: Member) => { if (confirm(`Remove ${m.name ?? m.email} from this organization?`)) act(() => api(`${base}/${m.user_id}`, { method: "DELETE" }), "Member removed."); };

  return (
    <div className="space-y-6">
      <ErrorNote msg={err} />
      {note && <p role="status" className="rounded-lg border border-brand/30 bg-brand/10 px-3 py-2 text-sm">{note}</p>}
      <Card className="p-4">
        <form onSubmit={invite} className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1"><Input label="Invite by email" type="email" required placeholder="name@company.com" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></div>
          <label className="block text-sm"><span className="mb-1.5 block font-medium">Role</span>
            <select value={f.role} onChange={(e) => setF({ ...f, role: e.target.value })} className="h-10 w-full rounded-lg border border-line glass px-3 sm:w-36">
              {ROLES.map((r) => <option key={r.v} value={r.v}>{r.l}</option>)}
            </select></label>
          <Button disabled={busy}><MailPlus className="h-4 w-4" />Send invite</Button>
        </form>
      </Card>
      <Card className="overflow-x-auto">
        {!list ? <div className="p-8 text-center"><Spinner className="mx-auto" /></div>
          : list.length === 0 ? <Empty title="No members yet" hint="Invite employees by email so they can use the assistant." />
          : (
            <table className="w-full text-sm">
              <thead className="border-b border-line text-left text-mute"><tr><th className="px-4 py-3 font-medium">Person</th><th className="px-4 py-3 font-medium">Role</th><th className="px-4 py-3 font-medium">Status</th><th className="w-12" /></tr></thead>
              <tbody className="divide-y divide-line">
                {list.map((m) => {
                  const me = m.user_id === user?.user_id;
                  return (
                    <tr key={m.user_id}>
                      <td className="px-4 py-3"><p className="font-medium">{m.name || m.email}{me && <span className="ml-2 text-xs font-normal text-mute">You</span>}</p>{m.name && <p className="text-mute">{m.email}</p>}</td>
                      <td className="px-4 py-3">
                        <select value={m.role.toLowerCase()} disabled={me} onChange={(e) => setRole(m, e.target.value)} aria-label={`Role for ${m.email}`} className="h-9 rounded-lg border border-line glass px-2 disabled:opacity-60">
                          {ROLES.map((r) => <option key={r.v} value={r.v}>{r.l}</option>)}
                          {!ROLES.some((r) => r.v === m.role.toLowerCase()) && <option value={m.role.toLowerCase()}>{m.role}</option>}
                        </select>
                      </td>
                      <td className="px-4 py-3"><span className="rounded-full bg-line px-2 py-0.5 text-xs">{m.status ?? "active"}</span></td>
                      <td className="px-2"><button disabled={me} onClick={() => remove(m)} aria-label={`Remove ${m.email}`} className="rounded p-2 text-mute hover:text-red-500 disabled:opacity-30"><Trash2 className="h-4 w-4" /></button></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
      </Card>
    </div>
  );
}
