'use client';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export default function DownloadPage() {
  const { id } = useParams<{ id: string }>();
  const [confetti, setConfetti] = useState(false);

  useEffect(() => {
    setConfetti(true);
  }, []);

  async function download() {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/jobs/${id}/download`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `edit-ai-job-${id}.mp4`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="relative min-h-[80vh] flex flex-col items-center justify-center p-4">
      {/* Background Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-4xl bg-gradient-to-b from-brand-violet/20 via-transparent to-transparent pointer-events-none blur-3xl"></div>

      {confetti && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {/* Simple confetti simulation using CSS particles */}
          {[...Array(20)].map((_, i) => (
            <div key={i} className="absolute animate-[fall_3s_infinite_linear]" style={{
              left: `${Math.random() * 100}%`,
              top: '-10%',
              backgroundColor: ['#22d3ee', '#8b5cf6', '#d946ef'][i % 3],
              width: '8px',
              height: '8px',
              animationDelay: `${Math.random() * 2}s`,
              opacity: 0.7
            }}></div>
          ))}
        </div>
      )}

      <div className="text-center space-y-8 max-w-2xl relative z-10 animate-in fade-in slide-in-from-bottom-5 duration-700">

        <div className="inline-block p-4 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-4 shadow-[0_0_30px_rgba(16,185,129,0.2)]">
          <svg className="w-16 h-16 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        <h1 className="text-4xl md:text-5xl font-bold text-white text-glow">
          It&apos;s a Wrap! Studio
        </h1>

        <p className="text-lg text-slate-300 leading-relaxed">
          Your video has been directed, cut, colored, and polished by your AI team.
          <span className="block mt-2 text-slate-400 text-sm">(And the QC Agent approved it!)</span>
        </p>

        <div className="grid grid-cols-3 gap-4 border-y border-slate-800 py-8">
          <div>
            <div className="text-3xl font-bold text-brand-cyan">100%</div>
            <div className="text-xs uppercase tracking-widest text-slate-500 mt-1">AI Generated</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-brand-violet">4K</div>
            <div className="text-xs uppercase tracking-widest text-slate-500 mt-1">Ready</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-brand-fuchsia">Viral</div>
            <div className="text-xs uppercase tracking-widest text-slate-500 mt-1">Potential</div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <button
            onClick={download}
            className="btn-primary px-8 py-4 text-lg shadow-[0_0_40px_rgba(34,211,238,0.3)] hover:shadow-[0_0_60px_rgba(34,211,238,0.5)] transform hover:scale-105 transition-all"
          >
            Download Master File
          </button>

          <button className="px-8 py-4 rounded-xl border border-slate-700 hover:bg-slate-800 text-slate-300 font-semibold transition-colors">
            Start New Project
          </button>
        </div>
      </div>

      <style jsx>{`
          @keyframes fall {
             0% { transform: translateY(0) rotate(0deg); opacity: 1; }
             100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
          }
       `}</style>
    </div>
  );
}
