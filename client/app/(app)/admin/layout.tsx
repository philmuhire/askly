"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { isAdmin, loading } = useAuth(); const r = useRouter();
  useEffect(() => { if (!loading && !isAdmin) r.replace("/chat"); }, [loading, isAdmin, r]);
  return isAdmin ? <div className="mx-auto max-w-5xl p-6 md:p-10">{children}</div> : null;
}
