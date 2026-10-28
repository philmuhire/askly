"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Building2, ChevronRight } from "lucide-react";
import { api } from "@/lib/api";
import { Button, Card, Empty, ErrorNote, Input, Spinner } from "@/components/ui";

type Org = { id: string; name: string; slug: string; plan: string; is_active: boolean; created_at: string };

export default function Platform() {
  const [orgs, setOrgs] = useState<Org[] | null>(null);
  const [f, setF] = useState({ name: "", slug: "", plan: "free" });
  const [err, setErr] = useState(""); const [busy, setBusy] = useState(false);
  const load = () => api<Org[]>("/organizations/").then(setOrgs).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);
  const create = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setErr("");
    try { await api("/organizations/", { method: "POST", body: JSON.stringify(f) }); setF({ name: "", slug: "", plan: "free" }); await load(); }
    catch (x: any) { setErr(x.message); } finally { setBusy(false); }
  };
  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-display text-3xl font-semibold">Tenants</h1>
        <p className="mt-1 text-mute">{orgs ? `${orgs.length} total, ${orgs.filter((o) => o.is_active).length} active` : "Loading…"}</p>
      </header>
      <ErrorNote msg={err} />
      <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
        <Card className="divide-y divide-line">
          {!orgs ? <div className="p-8 text-center"><Spinner className="mx-auto" /></div>
            : orgs.length === 0 ? <Empty title="No tenants yet" hint="Create the first organization using the form." />
            : orgs.map((o) => (
              <Link key={o.id} href={`/admin/${o.id}`} className="flex items-center gap-3 px-4 py-3.5 hover:bg-line/40">
                <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand/10 text-brand-text"><Building2 className="h-4 w-4" /></span>
                <span className="min-w-0 flex-1"><span className="block truncate font-medium">{o.name}</span><span className="text-sm text-mute">{o.slug} · {o.plan} plan</span></span>
                {!o.is_active && <span className="rounded-full bg-line px-2 py-0.5 text-xs">Inactive</span>}
                <ChevronRight className="h-4 w-4 text-mute" />
              </Link>
            ))}
        </Card>
        <Card className="h-fit p-4">
          <form onSubmit={create} className="space-y-3">
            <h2 className="font-display text-lg font-semibold">New organization</h2>
            <Input label="Name" required value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
            <Input label="Slug" required pattern="[a-z0-9\-]+" title="Lowercase letters, numbers and hyphens" value={f.slug} onChange={(e) => setF({ ...f, slug: e.target.value })} />
            <label className="block text-sm"><span className="mb-1.5 block font-medium">Plan</span>
              <select value={f.plan} onChange={(e) => setF({ ...f, plan: e.target.value })} className="h-10 w-full rounded-lg border border-line glass px-3">
                <option value="free">Free</option><option value="pro">Pro</option><option value="enterprise">Enterprise</option>
              </select></label>
            <Button className="w-full" disabled={busy}>Create organization</Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
