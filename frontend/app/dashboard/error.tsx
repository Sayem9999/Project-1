'use client';

import { useEffect } from 'react';
import { RefreshCcw, AlertCircle, Home } from 'lucide-react';
import Link from 'next/link';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Dashboard Crash:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] p-8 text-center bg-obsidian-950/50 rounded-3xl border border-red-500/20 backdrop-blur-xl">
      <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mb-6 text-red-500 animate-pulse">
        <AlertCircle className="w-8 h-8" />
      </div>
      
      <h1 className="text-2xl font-bold text-white mb-2 font-display">Something went wrong in the Studio</h1>
      <p className="text-gray-400 max-w-md mb-8 leading-relaxed">
        The dashboard encountered an unexpected error. This might be due to a connection issue or a rendering glitch.
      </p>

      <div className="flex flex-col sm:flex-row gap-4">
        <button
          onClick={() => reset()}
          className="flex items-center gap-2 px-6 py-3 rounded-full bg-white text-black font-bold hover:scale-105 transition-transform active:scale-95"
        >
          <RefreshCcw className="w-4 h-4" />
          Try Again
        </button>
        
        <Link 
          href="/"
          className="flex items-center gap-2 px-6 py-3 rounded-full bg-white/5 border border-white/10 text-white font-medium hover:bg-white/10 transition-colors"
        >
          <Home className="w-4 h-4" />
          Go Home
        </Link>
      </div>

      {error.digest && (
        <div className="mt-12 pt-6 border-t border-white/5 w-full">
          <p className="text-[10px] text-gray-600 font-mono tracking-widest uppercase mb-1">Error Signature</p>
          <p className="text-[10px] text-gray-800 font-mono italic">{error.digest}</p>
        </div>
      )}
    </div>
  );
}
