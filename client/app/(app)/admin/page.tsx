"use client";
import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Building2, ChevronRight } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { Card, Empty } from "@/components/ui";

export default function AdminHome() {
  const { user, isSuperAdmin } = useAuth(); const r = useRouter();
  const mine = (user?.organizations ?? []).filter((o) => ["admin", "owner"].includes(o.role.toLowerCase()));
  useEffect(() => { if (mine.length === 1 && !isSuperAdmin) r.replace(`/admin/${mine[0].organization_id}`); }, [mine.length, isSuperAdmin, r]); // eslint-disable-line
  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-semibold">Your organizations</h1>
      <Card className="divide-y divide-line">
        {mine.length === 0 ? <Empty title="No organizations to manage" hint={isSuperAdmin ? "Open Platform to manage any tenant." : "Ask a platform admin to make you an admin."} />
          : mine.map((o) => (
            <Link key={o.organization_id} href={`/admin/${o.organization_id}`} className="flex items-center gap-3 px-4 py-3.5 hover:bg-line/40">
              <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand/10 text-brand-text"><Building2 className="h-4 w-4" /></span>
              <span className="flex-1 font-medium">{o.name ?? o.organization_id}</span><ChevronRight className="h-4 w-4 text-mute" />
            </Link>))}
      </Card>
    </div>
  );
}
