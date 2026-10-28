"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, FileText, Upload } from "lucide-react";
import { api } from "@/lib/api";
import { Button, Card, Empty, ErrorNote, Input, Spinner, cn } from "@/components/ui";

type Sys = { id: string; name: string; description?: string | null; system_type: string; is_active: boolean };

export default function OrgPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const [org, setOrg] = useState<any>(null);
  const [systems, setSystems] = useState<Sys[] | null>(null);
  const [sel, setSel] = useState<Sys | null>(null);
  const [docs, setDocs] = useState<any[] | null>(null);
  const [f, setF] = useState({ name: "", description: "", system_type: "it_support" });
  const [err, setErr] = useState(""); const [uploading, setUploading] = useState(false);
  const file = useRef<HTMLInputElement>(null);

  const loadSystems = useCallback(() => api<Sys[]>(`/organizations/${orgId}/systems`).then(setSystems).catch((e) => setErr(e.message)), [orgId]);
  const loadDocs = useCallback((id: string, quiet = false) => { if (!quiet) setDocs(null); api<any>(`/systems/${id}/documents`).then((d) => setDocs(Array.isArray(d) ? d : d?.documents ?? [])).catch((e) => setErr(e.message)); }, []);
  const indexing = !!sel && !!docs?.some((d) => /pend|process|queue|index|upload/i.test(d.status ?? ""));
  useEffect(() => { if (!indexing || !sel) return; const t = setTimeout(() => loadDocs(sel.id, true), 4000); return () => clearTimeout(t); }, [indexing, docs, sel, loadDocs]);
  useEffect(() => { api(`/organizations/${orgId}`).then(setOrg).catch((e) => setErr(e.message)); loadSystems(); }, [orgId, loadSystems]);

  const createSystem = async (e: React.FormEvent) => {
    e.preventDefault(); setErr("");
    try { await api(`/organizations/${orgId}/systems`, { method: "POST", body: JSON.stringify({ ...f, description: f.description || null }) }); setF({ name: "", description: "", system_type: "it_support" }); loadSystems(); }
    catch (x: any) { setErr(x.message); }
  };
  const upload = async (files: FileList | null) => {
    if (!files?.length || !sel) return;
    setUploading(true); setErr("");
    try { for (const fl of Array.from(files)) { const fd = new FormData(); fd.append("file", fl); await api(`/systems/${sel.id}/documents`, { method: "POST", body: fd }); } loadDocs(sel.id); }
    catch (x: any) { setErr(x.message); } finally { setUploading(false); if (file.current) file.current.value = ""; }
  };

  return (
    <div className="space-y-6">
      <ErrorNote msg={err} />
      {systems?.length === 0 && (
        <Card className="p-5">
          <h2 className="font-display text-lg font-semibold">Set up your workspace</h2>
          <ol className="mt-3 list-decimal space-y-1.5 pl-5 text-sm text-mute">
            <li>Add a knowledge base on the left.</li>
            <li>Upload your IT guides, runbooks and policies to it.</li>
            <li><Link href={`/admin/${orgId}/members`} className="text-brand-text underline-offset-4 hover:underline">Invite colleagues</Link> so they can ask questions.</li>
            <li><Link href="/chat" className="text-brand-text underline-offset-4 hover:underline">Try the assistant</Link> yourself.</li>
          </ol>
        </Card>
      )}
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
        <div className="space-y-4">
          <Card className="divide-y divide-line">
            {!systems ? <div className="p-6 text-center"><Spinner className="mx-auto" /></div>
              : systems.length === 0 ? <Empty title="No knowledge bases" hint="Add one below, then upload your IT documents." />
              : systems.map((s) => (
                <button key={s.id} onClick={() => { setSel(s); loadDocs(s.id); }} className={cn("block w-full px-4 py-3 text-left", sel?.id === s.id ? "bg-brand/10" : "hover:bg-line/40")}>
                  <span className="block font-medium">{s.name}</span><span className="text-sm text-mute">{s.system_type}</span>
                </button>
              ))}
          </Card>
          <Card className="p-4">
            <form onSubmit={createSystem} className="space-y-3">
              <h2 className="font-display text-lg font-semibold">Add a knowledge base</h2>
              <Input label="Name" required value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
              <label className="block text-sm"><span className="mb-1.5 block font-medium">Type</span>
                <select value={f.system_type} onChange={(e) => setF({ ...f, system_type: e.target.value })} className="h-10 w-full rounded-lg border border-line glass px-3">
                  <option value="it_support">IT helpdesk</option><option value="network">Network and VPN</option><option value="policies">Security policies</option><option value="onboarding">Device onboarding</option>
                </select></label>
              <Input label="Description" value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} />
              <Button className="w-full">Add knowledge base</Button>
            </form>
          </Card>
        </div>
        <Card className="min-h-64">
          {!sel ? <Empty title="Select a system" hint="Pick a knowledge base on the left to manage its documents." /> : (
            <>
              <div className="flex items-center justify-between border-b border-line p-4">
                <div><h2 className="font-display text-lg font-semibold">{sel.name} documents</h2><p className="text-sm text-mute">Guides, runbooks and policies (PDF, Word, text, Markdown). New files are indexed before the assistant can cite them.</p></div>
                <input ref={file} type="file" multiple hidden accept=".pdf,.docx,.txt,.md" onChange={(e) => upload(e.target.files)} />
                <Button onClick={() => file.current?.click()} disabled={uploading}>{uploading ? <Spinner className="text-brand-ink" /> : <Upload className="h-4 w-4" />}Upload documents</Button>
              </div>
              {!docs ? <div className="p-8 text-center"><Spinner className="mx-auto" /></div>
                : docs.length === 0 ? <Empty title="No documents yet" hint="Upload troubleshooting guides, runbooks or policies to get started." />
                : <ul className="divide-y divide-line">{docs.map((d) => (
                    <li key={d.id} className="flex items-center gap-3 px-4 py-3">
                      <FileText className="h-4 w-4 text-brand-text" />
                      <span className="min-w-0 flex-1 truncate">{d.filename ?? d.title ?? d.name ?? d.id}</span>
                      {d.status && <span className="rounded-full bg-line px-2 py-0.5 text-xs">{d.status}</span>}
                    </li>))}</ul>}
            </>
          )}
        </Card>
      </div>
    </div>
  );
}
