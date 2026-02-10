"use client";
import { useCallback, useEffect, useState } from "react";
import { API_ORIGIN } from "@/lib/api";

export default function SystemBanner() {
  const [status, setStatus] = useState<"checking" | "ok" | "down">("checking");

  const checkHealth = useCallback(async () => {
    try {
      const res = await fetch(`${API_ORIGIN}/health`, { cache: "no-store" });
      if (!res.ok) throw new Error("health failed");
      const data = await res.json();
      const ok = data?.status === "healthy" || data?.status === "ok";
      setStatus(ok ? "ok" : "down");
    } catch {
      setStatus("down");
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  if (status !== "down") return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-[60] bg-red-500/20 border-b border-red-500/40 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 py-2 flex items-center justify-between text-xs sm:text-sm text-red-200">
        <span className="font-semibold">Backend is unreachable. Some actions may fail.</span>
        <button
          onClick={checkHealth}
          className="px-3 py-1 rounded-md bg-red-500/30 hover:bg-red-500/40 text-red-100 transition-colors"
        >
          Retry
        </button>
      </div>
    </div>
  );
}
