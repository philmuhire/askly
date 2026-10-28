"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { homeFor, useAuth } from "@/lib/auth";
import { Spinner } from "@/components/ui";

export default function Home() {
  const { user, loading } = useAuth();
  const r = useRouter();
  useEffect(() => {
    if (!loading) r.replace(user ? homeFor(user) : "/login");
  }, [loading, user, r]);
  return (
    <div className="grid min-h-screen place-items-center">
      <Spinner />
    </div>
  );
}
