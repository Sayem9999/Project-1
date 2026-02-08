'use client';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ThemeSelector } from '@/components/ui/ThemeSelector';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [theme, setTheme] = useState('professional');
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const router = useRouter();

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const token = localStorage.getItem('token');
    const form = new FormData();
    form.append('file', file);
    form.append('theme', theme);

    try {
      const res = await fetch(`${API_BASE}/jobs/upload`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form
      });

      if (!res.ok) {
        throw new Error('Upload failed');
      }

      const data = await res.json();
      router.push(`/dashboard/jobs/${data.id}`);
    } catch (e) {
      setError('Upload failed. Please try again.');
      setUploading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="glass-panel relative overflow-hidden rounded-2xl p-8">
        <div className="absolute -top-24 -right-24 h-48 w-48 rounded-full bg-brand-cyan/20 blur-3xl"></div>
        <div className="absolute top-1/2 -left-24 h-48 w-48 rounded-full bg-brand-magenta/20 blur-3xl"></div>

        <section className="relative space-y-2 mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-white text-glow">
            Upload Source Video
          </h1>
          <p className="text-slate-400">
            AI Director will analyze your footage and apply the selected editing style.
          </p>
        </section>

        <form onSubmit={submit} className="relative space-y-8">
          <ThemeSelector value={theme} onChange={setTheme} />

          <div className="space-y-3">
            <label className="text-sm font-medium text-slate-400">Source File</label>
            <div className="flex w-full items-center justify-center">
              <label className={`flex h-32 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed transition-all ${file ? 'border-brand-cyan bg-brand-cyan/5' : 'border-slate-700 bg-slate-900/50 hover:bg-slate-900'}`}>
                <div className="flex flex-col items-center justify-center pb-6 pt-5">
                  {file ? (
                    <>
                      <div className="text-brand-cyan mb-2">
                        <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                      </div>
                      <p className="mb-2 text-sm text-slate-300 font-medium">{file.name}</p>
                      <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </>
                  ) : (
                    <>
                      <div className="text-slate-500 mb-2">
                        <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                      </div>
                      <p className="mb-2 text-sm text-slate-400"><span className="font-semibold text-brand-cyan">Click to upload</span> or drag and drop</p>
                      <p className="text-xs text-slate-500">MP4, MOV up to 500MB</p>
                    </>
                  )}
                </div>
                <input type="file" className="hidden" accept="video/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
              </label>
            </div>
          </div>

          <div className="pt-4">
            <button
              disabled={!file || uploading}
              className={`w-full rounded-lg bg-gradient-to-r from-brand-cyan to-brand-violet px-5 py-4 font-bold text-white shadow-lg transition-all hover:shadow-brand-cyan/25 ${(!file || uploading) ? 'opacity-50 cursor-not-allowed' : 'hover:scale-[1.02] active:scale-[0.98]'
                }`}
            >
              {uploading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  Processing...
                </span>
              ) : (
                'Start Production'
              )}
            </button>
            {error && <p className="mt-4 text-center text-sm text-red-400">{error}</p>}
          </div>
        </form>
      </div>
    </div>
  );
}
