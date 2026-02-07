'use client';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState('');
  const router = useRouter();

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    const token = localStorage.getItem('token');
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${API_BASE}/jobs/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form
    });
    if (!res.ok) return setError('Upload failed');
    const data = await res.json();
    router.push(`/jobs/${data.id}`);
  }

  return <form onSubmit={submit} className="space-y-4"><h1 className="text-3xl font-semibold">Upload source video</h1><p className="text-slate-300">Best for podcast episodes, interviews, and expert talking-head content.</p><input type="file" accept="video/*" onChange={(e)=>setFile(e.target.files?.[0] ?? null)} className="block" /><button className="rounded bg-cyan-400 px-5 py-3 font-semibold text-slate-950">Start processing</button><p className="text-red-400">{error}</p></form>;
}
