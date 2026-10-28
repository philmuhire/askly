"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { FileText, Plus, SendHorizonal, Trash2 } from "lucide-react";
import { api, streamChat } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { KeyRound, Laptop, ShieldCheck, Wifi } from "lucide-react";
import { Button, Card, ErrorNote, Input, Orb, cn } from "@/components/ui";

type Source = {
  id: string;
  title: string;
  page_number?: number | null;
  snippet: string;
};
type Msg = {
  id: string;
  role: string;
  content: string;
  sources?: Source[] | null;
};
type Conv = { id: string; title?: string | null };

function ChatView() {
  const { activeOrgId } = useAuth();
  const [convs, setConvs] = useState<Conv[]>([]);
  const [cid, setCid] = useState<string | null>(null);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [steps, setSteps] = useState<string[]>([]);
  const [err, setErr] = useState("");
  const end = useRef<HTMLDivElement>(null);

  const loadList = useCallback(
    () =>
      api<Conv[]>(
        "/api/v1/chat/conversations" +
          (activeOrgId ? `?organization_id=${activeOrgId}` : ""),
      )
        .then(setConvs)
        .catch(() => {}),
    [activeOrgId],
  );
  const open = useCallback(async (id: string) => {
    setCid(id);
    const d = await api("/api/v1/chat/conversations/" + id + "/" + activeOrgId);
    setMsgs(d.messages);
  }, []);
  useEffect(() => {
    setCid(null);
    setMsgs([]);
    setErr("");
  }, [activeOrgId]);
  useEffect(() => {
    loadList();
  }, [loadList]);
  useEffect(() => {
    end.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, steps]);

  const send = async (override?: string) => {
    const text = (override ?? input).trim();
    if (!text || busy) return;
    setInput("");
    setErr("");
    setSteps([]);
    setBusy(true);
    let id = cid;
    setMsgs((m) => [
      ...m,
      { id: "u" + Date.now(), role: "user", content: text },
      { id: "a" + Date.now(), role: "assistant", content: "" },
    ]);
    await streamChat(text, cid, activeOrgId, {
      meta: (d) => {
        id = d?.conversation_id ?? id;
        if (id) setCid(id);
      },
      status: (s) =>
        s && setSteps((p) => (p[p.length - 1] === s ? p : [...p, s])),
      token: (t) =>
        setMsgs((m) =>
          m.map((x, i) =>
            i === m.length - 1 ? { ...x, content: x.content + t } : x,
          ),
        ),
      error: (e) => setErr(e),
    });
    setBusy(false);
    setSteps([]);
    if (id) {
      await open(id).catch(() => {});
      loadList();
    }
  };
  const remove = async (id: string) => {
    await api(`/api/v1/chat/conversations/${id}/${activeOrgId}`, {
      method: "DELETE",
    });
    if (id === cid) {
      setCid(null);
      setMsgs([]);
    }
    loadList();
  };

  return (
    <div className="flex h-[calc(100dvh-3.75rem)] md:h-screen">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-line lg:flex">
        <div className="p-3">
          <Button
            variant="outline"
            className="w-full"
            onClick={() => {
              setCid(null);
              setMsgs([]);
            }}
          >
            <Plus className="h-4 w-4" />
            New chat
          </Button>
        </div>
        <ul className="flex-1 space-y-0.5 overflow-y-auto px-2 pb-3">
          {convs.map((c) => (
            <li
              key={c.id}
              className={cn(
                "group flex items-center rounded-lg",
                c.id === cid ? "bg-brand/10" : "hover:bg-line/50",
              )}
            >
              <button
                onClick={() => open(c.id)}
                className="min-w-0 flex-1 truncate px-3 py-2 text-left text-sm"
              >
                {c.title || "Untitled chat"}
              </button>
              <button
                onClick={() => remove(c.id)}
                aria-label="Delete chat"
                className="mr-1 hidden rounded p-1.5 text-mute hover:text-red-500 group-hover:block"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </li>
          ))}
        </ul>
      </aside>
      <section className="flex min-w-0 flex-1 flex-col">
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto max-w-2xl space-y-6">
            {msgs.length === 0 && (
              <div className="pt-[10vh] text-center">
                <div className="mb-8 flex justify-center">
                  <Orb lg />
                </div>
                <h1 className="font-display text-4xl font-semibold">
                  Hi, I’m your IT assistant.
                </h1>
                <p className="mx-auto mt-2 max-w-md text-mute">
                  What’s going wrong? Describe the problem in plain words.
                  Answers come from your organization’s IT documentation and
                  cite the source.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {[
                    [Wifi, "I can’t connect to the VPN"],
                    [KeyRound, "How do I reset my password?"],
                    [Laptop, "Set up my new laptop"],
                    [ShieldCheck, "What is the BYOD policy?"],
                  ].map(([Icon, q]: any) => (
                    <button
                      key={q}
                      onClick={() => send(q)}
                      className="glass flex items-center gap-2.5 rounded-full border border-line py-1.5 pl-1.5 pr-4 text-sm hover:border-brand/60"
                    >
                      <span className="grid h-8 w-8 place-items-center rounded-full bg-brand/20 text-brand-text">
                        <Icon className="h-4 w-4" />
                      </span>
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {msgs.map((m) => (
              <div
                key={m.id}
                className={cn(
                  "flex items-start gap-3",
                  m.role === "user" && "justify-end",
                )}
              >
                {m.role !== "user" && <Orb />}
                <div
                  className={cn(
                    "min-w-0 max-w-[85%] whitespace-pre-wrap rounded-2xl border px-4 py-3 leading-relaxed",
                    m.role === "user"
                      ? "border-brand/40 bg-brand/20"
                      : "glass border-line",
                  )}
                >
                  {m.content ||
                    (busy ? (
                      <ul
                        className="space-y-1 text-sm text-mute"
                        aria-live="polite"
                      >
                        {(steps.length
                          ? steps
                          : ["Reading your question…"]
                        ).map((s, i, a) => (
                          <li key={i} className="flex items-center gap-2">
                            <span
                              className={cn(
                                "h-1.5 w-1.5 rounded-full",
                                i === a.length - 1
                                  ? "animate-pulse bg-brand"
                                  : "bg-line",
                              )}
                            />
                            {s}
                          </li>
                        ))}
                      </ul>
                    ) : null)}
                  {!!m.sources?.length && (
                    <div className="mt-3 space-y-1.5">
                      {m.sources.map((s) => (
                        <details
                          key={s.id}
                          className="rounded-lg border border-line glass text-sm"
                        >
                          <summary className="flex cursor-pointer items-center gap-2 px-3 py-2">
                            <FileText className="h-4 w-4 text-brand-text" />
                            <span className="truncate">{s.title}</span>
                            {s.page_number != null && (
                              <span className="ml-auto shrink-0 text-xs text-mute">
                                page {s.page_number}
                              </span>
                            )}
                          </summary>
                          <p className="border-t border-line px-3 py-2 text-mute">
                            {s.snippet}
                          </p>
                        </details>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={end} />
          </div>
        </div>
        <div className="p-4">
          <div className="mx-auto max-w-2xl space-y-2">
            <ErrorNote msg={err} />
            <div className="flex items-end gap-2 rounded-3xl border border-line glass p-2 shadow-[0_20px_60px_-30px_rgb(var(--brand)/.8)]">
              <textarea
                rows={1}
                maxLength={4000}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Describe your IT issue…"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }}
                className="max-h-40 min-h-10 flex-1 resize-none bg-transparent px-2 py-2 outline-none"
              />
              <Button
                onClick={() => send()}
                disabled={busy || !input.trim()}
                aria-label="Send"
                className="w-10 px-0"
              >
                <SendHorizonal className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function SetupWorkspace() {
  const { user, reloadSession } = useAuth();
  const [name, setName] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setErr("");
    const slug =
      name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "") +
      "-" +
      Math.random().toString(36).slice(2, 6);
    try {
      await api("/organizations/", {
        method: "POST",
        body: JSON.stringify({ name, slug, plan: "free" }),
      });
      await reloadSession();
    } catch (x: any) {
      setErr(x.message);
      setBusy(false);
    }
  };
  return (
    <div className="grid min-h-screen place-items-center p-6">
      <Card className="w-full max-w-md p-6">
        <form onSubmit={create} className="space-y-4">
          <h1 className="font-display text-2xl font-semibold">
            Welcome, {user?.name.split(" ")[0]}
          </h1>
          <p className="text-mute">
            Your account isn’t part of an organization yet. Name your workspace
            to start adding IT documents and colleagues, or ask an admin to
            invite you to an existing one.
          </p>
          <ErrorNote msg={err} />
          <Input
            label="Organization name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Button className="w-full" disabled={busy || !name.trim()}>
            Create workspace
          </Button>
        </form>
      </Card>
    </div>
  );
}

export default function Chat() {
  const { user } = useAuth();
  return user && user.organizations.length === 0 ? (
    <SetupWorkspace />
  ) : (
    <ChatView />
  );
}
