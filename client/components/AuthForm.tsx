"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { homeFor, useAuth } from "@/lib/auth";
import { Button, ErrorNote, Input, Orb } from "./ui";
import ThemeToggle from "./ThemeToggle";

export default function AuthForm({ mode }: { mode: "login" | "register" }) {
  const { login, register } = useAuth();
  const r = useRouter();
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [err, setErr] = useState(""); const [busy, setBusy] = useState(false);
  const reg = mode === "register";
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setErr("");
    try {
      const u = reg ? await register(f.name, f.email, f.password) : await login(f.email, f.password);
      r.replace(homeFor(u));
    } catch (x: any) { setErr(x.message); } finally { setBusy(false); }
  };
  return (
    <main className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      <section className="hidden flex-col justify-between border-r border-line bg-gradient-to-br from-brand/35 via-brand/10 to-transparent p-12 lg:flex">
        <p className="font-display text-xl font-semibold">IT Support Assistant</p>
        <div>
          <div className="mb-8"><Orb lg /></div>
          <h1 className="font-display text-5xl font-semibold leading-[1.05]">Fix it faster.<br />Answers from your own IT docs.</h1>
          <p className="mt-5 max-w-md opacity-80">Ask about VPN, passwords, devices or policy. Every reply is built from your organization’s troubleshooting guides and cites the page it used.</p>
        </div>
        <p className="text-sm opacity-70">Each organization’s documents and chats are kept separate from every other tenant.</p>
      </section>
      <section className="relative flex items-center justify-center p-6">
        <div className="absolute right-4 top-4"><ThemeToggle /></div>
        <form onSubmit={submit} className="w-full max-w-sm space-y-4">
          <h2 className="font-display text-3xl font-semibold">{reg ? "Create your account" : "Sign in"}</h2>
          <ErrorNote msg={err} />
          {reg && <Input label="Full name" required value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />}
          <Input label="Email" type="email" required autoComplete="email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} />
          <Input label="Password" type="password" required autoComplete={reg ? "new-password" : "current-password"} value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} />
          <Button className="w-full" disabled={busy}>{busy ? "Please wait…" : reg ? "Create account" : "Sign in"}</Button>
          <p className="text-sm text-mute">
            {reg ? "Already have an account? " : "New here? "}
            <Link className="font-medium text-brand-text underline-offset-4 hover:underline" href={reg ? "/login" : "/register"}>{reg ? "Sign in" : "Create an account"}</Link>
          </p>
        </form>
      </section>
    </main>
  );
}
