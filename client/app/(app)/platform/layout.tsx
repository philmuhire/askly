"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function PlatformLayout({ children }: { children: React.ReactNode }) {
  const { isSuperAdmin, loading } = useAuth(); const r = useRouter();
  useEffect(() => { if (!loading && !isSuperAdmin) r.replace("/chat"); }, [loading, isSuperAdmin, r]);
  return isSuperAdmin ? <div className="mx-auto max-w-5xl p-6 md:p-10">{children}</div> : null;
}
