"use client";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, refreshSession, tokens } from "./api";

export type Membership = { organization_id: string; name?: string | null; role: string };
export type User = { user_id: string; name: string; email: string; is_super_admin?: boolean; organizations: Membership[] };
const ADMIN = ["admin", "owner"];
export const superOf = (u: User | null) => !!u && (!!u.is_super_admin || u.organizations.some((o) => o.role.toLowerCase() === "super_admin"));
export const adminOf = (u: User | null) => !!u && (superOf(u) || u.organizations.some((o) => ADMIN.includes(o.role.toLowerCase())));
export const homeFor = (u: User | null) => (superOf(u) ? "/platform" : adminOf(u) ? "/admin" : "/chat");
type Ctx = { user: User | null; loading: boolean; isAdmin: boolean; isSuperAdmin: boolean; login: (e: string, p: string) => Promise<User>; register: (n: string, e: string, p: string) => Promise<User>; logout: () => void; reloadSession: () => Promise<void>; activeOrgId: string | null; setActiveOrg: (id: string) => void };
const AuthCtx = createContext<Ctx>(null as any);
export const useAuth = () => useContext(AuthCtx);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [pref, setPref] = useState<string | null>(null);
  useEffect(() => {
    try { const u = localStorage.getItem("sa_user"); if (u && tokens.access()) setUser(JSON.parse(u)); } catch {}
    setPref(localStorage.getItem("sa_org"));
    setLoading(false);
  }, []);
  const login = useCallback(async (email: string, password: string) => {
    const d = await api("/auth/signin", { method: "POST", body: JSON.stringify({ email, password }) });
    tokens.set(d.access_token, d.refresh_token);
    const u: User = { user_id: d.user_id, name: d.name, email: d.email, is_super_admin: d.is_super_admin ?? d.is_superuser ?? false, organizations: d.organizations };
    localStorage.setItem("sa_user", JSON.stringify(u)); setUser(u); return u;
  }, []);
  const register = useCallback(async (name: string, email: string, password: string) => {
    await api("/auth/", { method: "POST", body: JSON.stringify({ name, email, password }) });
    return login(email, password);
  }, [login]);
  const reloadSession = useCallback(async () => {
    const d = await refreshSession();
    if (!d) return;
    setUser((prev) => {
      const u: User = { user_id: d.user_id, name: d.name, email: d.email, is_super_admin: d.is_super_admin ?? prev?.is_super_admin ?? false, organizations: d.organizations };
      localStorage.setItem("sa_user", JSON.stringify(u)); return u;
    });
  }, []);
  const logout = useCallback(() => { tokens.clear(); setUser(null); window.location.href = "/login"; }, []);
  const activeOrgId = user?.organizations.find((o) => o.organization_id === pref)?.organization_id ?? user?.organizations[0]?.organization_id ?? null;
  const setActiveOrg = (id: string) => { localStorage.setItem("sa_org", id); setPref(id); };
  const isAdmin = adminOf(user), isSuperAdmin = superOf(user);
  return <AuthCtx.Provider value={{ user, loading, isAdmin, isSuperAdmin, login, register, logout, reloadSession, activeOrgId, setActiveOrg }}>{children}</AuthCtx.Provider>;
}
