"use client";
import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Building2, LayoutDashboard, LogOut, MessageSquare } from "lucide-react";
import { useAuth } from "@/lib/auth";
import ThemeToggle from "@/components/ThemeToggle";
import { Spinner, cn } from "@/components/ui";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, isAdmin, isSuperAdmin, logout, activeOrgId, setActiveOrg } = useAuth();
  const r = useRouter(); const path = usePathname();
  useEffect(() => { if (!loading && !user) r.replace("/login"); }, [loading, user, r]);
  if (!user) return <div className="grid min-h-screen place-items-center"><Spinner /></div>;
  const activeRole = user.organizations.find((o) => o.organization_id === activeOrgId)?.role.toLowerCase() ?? "";
  const activeAdmin = ["admin", "owner"].includes(activeRole);
  const nav: { href: string; match?: string; label: string; Icon: any }[] = [{ href: "/chat", label: "Assistant", Icon: MessageSquare }, ...(isAdmin ? [{ href: activeAdmin ? `/admin/${activeOrgId}` : "/admin", match: "/admin", label: "Admin", Icon: LayoutDashboard }] : []), ...(isSuperAdmin ? [{ href: "/platform", label: "Platform", Icon: Building2 }] : [])];
  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="flex items-center gap-2 border-b border-line glass p-3 sticky top-0 z-20 md:h-screen md:w-60 md:flex-col md:items-stretch md:border-b-0 md:border-r md:p-4">
        <p className="mr-2 font-display text-lg font-semibold md:mr-0">IT Support</p>
        {user.organizations.length > 1 ? (
          <select value={activeOrgId ?? ""} onChange={(e) => setActiveOrg(e.target.value)} aria-label="Organization" className="h-9 min-w-0 max-w-[9rem] rounded-lg border border-line bg-bg px-2 text-sm md:mb-3 md:max-w-none">
            {user.organizations.map((o) => <option key={o.organization_id} value={o.organization_id}>{o.name ?? o.organization_id}</option>)}
          </select>
        ) : user.organizations[0]?.name ? <p className="hidden truncate text-sm text-mute md:mb-3 md:block">{user.organizations[0].name}</p> : null}
        <nav className="flex flex-1 gap-1 md:flex-col">
          {nav.map(({ href, match, label, Icon }) => (
            <Link key={href} href={href} className={cn("flex items-center gap-2 rounded-lg px-3 py-2 text-sm", path.startsWith(match ?? href) ? "bg-brand/20 font-medium text-brand-text" : "text-mute hover:bg-line/60 hover:text-ink")}>
              <Icon className="h-4 w-4" />{label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2 md:border-t md:border-line md:pt-3">
          <div className="hidden min-w-0 flex-1 md:block"><p className="truncate text-sm font-medium">{user.name}</p><p className="truncate text-xs text-mute">{user.email}</p></div>
          <ThemeToggle />
          <button onClick={logout} aria-label="Sign out" className="grid h-9 w-9 place-items-center rounded-lg text-mute hover:bg-line/60 hover:text-ink"><LogOut className="h-4 w-4" /></button>
        </div>
      </aside>
      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
