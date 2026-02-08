'use client';
import { FormEvent, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DirectorPanel } from '@/components/ui/DirectorPanel';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // Director Controls
  const [pacing, setPacing] = useState('medium');
  const [mood, setMood] = useState('professional');
  const [ratio, setRatio] = useState('16:9');

  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const token = localStorage.getItem('token');
    const form = new FormData();
    form.append('file', file);
    form.append('pacing', pacing);
    form.append('mood', mood);
    form.append('ratio', ratio);
    form.append('theme', mood);

    try {
      const res = await fetch(`${API_BASE}/jobs/upload`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form
      });

      if (!res.ok) {
        const errBody = await res.text();
        throw new Error(`Status ${res.status}: ${errBody}`);
      }

      const data = await res.json();
      router.push(`/jobs/${data.id}`);
    } catch (e) {
      console.error("Upload error:", e);
      // User-friendly error messages
      let errorMessage = 'Upload failed. Please try again.';
      if (e instanceof Error) {
        if (e.message.includes('401')) errorMessage = 'Session expired. Please log in again.';
        else if (e.message.includes('413')) errorMessage = 'File too large. Maximum size is 500MB.';
        else if (e.message.includes('Network')) errorMessage = 'Network error. Check your connection.';
        else if (e.message.includes('500')) errorMessage = 'Server error. Our team has been notified.';
        else errorMessage = e.message;
      }
      setError(errorMessage);
      setUploading(false);
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => setIsDragOver(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="glass-panel relative overflow-hidden rounded-2xl p-8">
        <div className="absolute -top-24 -right-24 h-48 w-48 rounded-full bg-brand-cyan/20 blur-3xl"></div>
        <div className="absolute top-1/2 -left-24 h-48 w-48 rounded-full bg-brand-violet/20 blur-3xl"></div>

        <section className="relative space-y-2 mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white text-glow">
            Start Production
          </h1>
          <p className="text-slate-400">
            Tell the AI Director how to edit your footage.
          </p>
        </section>

        <form onSubmit={submit} className="relative space-y-8">
          <DirectorPanel
            pacing={pacing} setPacing={setPacing}
            mood={mood} setMood={setMood}
            ratio={ratio} setRatio={setRatio}
          />

          <div className="space-y-3">
            <label className="text-sm font-medium text-slate-400">Source Footage</label>
            <div className="flex w-full items-center justify-center">
              <label
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`group flex h-48 w-full cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed transition-all duration-300 ${isDragOver
                  ? 'border-brand-cyan bg-brand-cyan/10 scale-102 ring-4 ring-brand-cyan/20'
                  : file
                    ? 'border-emerald-500/50 bg-emerald-500/5'
                    : 'border-slate-700 bg-slate-900/50 hover:bg-slate-900 hover:border-slate-500'
                  }`}
              >
                <div className="flex flex-col items-center justify-center pb-6 pt-5">
                  {file ? (
                    <div className="animate-in fade-in zoom-in duration-300 text-center">
                      <div className="mx-auto bg-emerald-500/20 p-4 rounded-full mb-3">
                        <svg className="h-8 w-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                      </div>
                      <p className="text-lg font-semibold text-white">{file.name}</p>
                      <p className="text-sm text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB • Ready for AI</p>
                    </div>
                  ) : (
                    <div className="text-center space-y-2">
                      <div className={`mx-auto p-4 rounded-full transition-all duration-300 ${isDragOver ? 'bg-brand-cyan/20 scale-110' : 'bg-slate-800'}`}>
                        <svg className={`h-8 w-8 transition-colors ${isDragOver ? 'text-brand-cyan' : 'text-slate-400 group-hover:text-white'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                      </div>
                      <div>
                        <p className="text-lg font-medium text-white group-hover:text-brand-cyan transition-colors">Click to upload</p>
                        <p className="text-sm text-slate-400">or drag and drop video files</p>
                      </div>
                      <p className="text-xs text-slate-600">MP4, MOV up to 500MB</p>
                    </div>
                  )}
                </div>
                <input type="file" className="hidden" accept="video/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
              </label>
            </div>
          </div>

          <div className="pt-4">
            <button
              disabled={!file || uploading}
              className={`w-full rounded-xl bg-gradient-to-r from-brand-cyan to-brand-violet px-5 py-5 text-lg font-bold text-white shadow-[0_0_30px_rgba(139,92,246,0.3)] transition-all hover:shadow-[0_0_50px_rgba(139,92,246,0.5)] ${(!file || uploading) ? 'opacity-50 cursor-not-allowed bg-slate-800' : 'hover:scale-[1.02] active:scale-[0.98]'
                }`}
            >
              {uploading ? (
                <span className="flex items-center justify-center gap-3">
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  Initializing AI Agents...
                </span>
              ) : (
                'Start Production'
              )}
            </button>
            {error && (
              <div className="mt-4 flex items-center justify-between gap-3 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm text-red-300">{error}</p>
                </div>
                <button onClick={() => setError('')} className="text-red-400 hover:text-red-300">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
