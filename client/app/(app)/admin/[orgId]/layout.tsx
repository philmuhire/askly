"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, usePathname, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { cn } from "@/components/ui";

export default function OrgLayout({ children }: { children: React.ReactNode }) {
  const { orgId } = useParams<{ orgId: string }>();
  const { user, isSuperAdmin } = useAuth(); const r = useRouter(); const path = usePathname();
  const [org, setOrg] = useState<any>(null);
  const allowed = isSuperAdmin || !!user?.organizations.some((o) => o.organization_id === orgId && ["admin", "owner"].includes(o.role.toLowerCase()));
  useEffect(() => { if (user && !allowed) r.replace("/admin"); }, [user, allowed, r]);
  useEffect(() => { if (allowed) api(`/organizations/${orgId}`).then(setOrg).catch(() => {}); }, [orgId, allowed]);
  if (!allowed) return null;
  const tabs = [{ href: `/admin/${orgId}`, label: "Knowledge bases" }, { href: `/admin/${orgId}/members`, label: "Members" }];
  return (
    <div className="space-y-8">
      <header>
        {isSuperAdmin && <Link href="/platform" className="mb-3 inline-flex items-center gap-1 text-sm text-mute hover:text-ink"><ArrowLeft className="h-4 w-4" />All tenants</Link>}
        <h1 className="font-display text-3xl font-semibold">{org?.name ?? "…"}</h1>
        {org && <p className="mt-1 text-mute">{org.slug} · {org.plan} plan</p>}
        <nav className="mt-5 flex gap-1 border-b border-line">
          {tabs.map((t) => (
            <Link key={t.href} href={t.href} className={cn("-mb-px border-b-2 px-3 pb-2.5 text-sm", path === t.href ? "border-brand font-medium text-ink" : "border-transparent text-mute hover:text-ink")}>{t.label}</Link>
          ))}
        </nav>
      </header>
      {children}
    </div>
  );
}
