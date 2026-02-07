'use client';
import { useParams } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export default function DownloadPage() {
  const { id } = useParams<{ id: string }>();

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

  return <section className="space-y-4"><h1 className="text-3xl font-semibold">Download final render</h1><p className="text-slate-300">Your export includes polished cuts, audio cleanup, and subtitle styling.</p><button onClick={download} className="rounded bg-cyan-400 px-5 py-3 font-semibold text-slate-950">Download .mp4</button></section>;
}
