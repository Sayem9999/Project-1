'use client';
import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, Sparkles, Zap, Video, CheckCircle2, X } from 'lucide-react';
import { apiUpload, apiRequest, ApiError, clearAuth } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

const VIBES = [
  { id: 'viral', label: 'Viral Moment', icon: <Zap className="w-5 h-5 text-yellow-400" />, theme: 'energetic', description: 'Fast-paced, high energy, perfect for social.' },
  { id: 'cinematic', label: 'Movie Feel', icon: <Video className="w-5 h-5 text-indigo-400" />, theme: 'cinematic', description: 'Deep colors, smooth transitions, atmospheric.' },
  { id: 'clean', label: 'Pro Minimalist', icon: <Sparkles className="w-5 h-5 text-cyan-400" />, theme: 'minimal', description: 'Polished, clear, and professional focus.' },
];

export default function CreatorPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedVibe, setSelectedVibe] = useState(VIBES[0]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile?.type.startsWith('video/')) {
      setFile(droppedFile);
      setPreview(URL.createObjectURL(droppedFile));
    }
  }, []);

  const handleGo = async () => {
    if (!file) return;
    setUploading(true);
    setProgress(0);
    setError('');

    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login?redirect=/creator');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('theme', selectedVibe.theme);
      formData.append('pacing', selectedVibe.id === 'viral' ? 'fast' : 'medium');
      formData.append('mood', selectedVibe.theme);
      formData.append('platform', 'social');
      formData.append('tier', 'pro');

      // 1. Upload
      const { promise } = apiUpload<{ id: number }>('/jobs/upload', {
        body: formData,
        auth: true,
        onProgress: (p) => setProgress(Math.floor(p * 0.8)), // 80% for upload
      });
      const job = await promise;

      // 2. Auto-Start
      setProgress(90);
      await apiRequest(`/jobs/${job.id}/start`, { method: 'POST', auth: true });
      setProgress(100);

      // 3. Redirect to Job Status
      router.push(`/jobs/${job.id}`);
    } catch (err: any) {
      if (err instanceof ApiError && err.isAuth) {
        clearAuth();
        router.push('/login?redirect=/creator');
        return;
      }
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Try a smaller file?');
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white pt-32 pb-20 px-6 overflow-hidden relative">
        {/* Background blobs */}
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-brand-cyan/10 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-brand-violet/10 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />

      <div className="max-w-4xl mx-auto relative z-10">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold mb-4 tracking-tight">
            Drop it. <span className="text-brand-cyan">Vibe it.</span> Done.
          </h1>
          <p className="text-gray-400 text-lg">The world&apos;s simplest editor. No timelines, just results.</p>
        </div>

        {!file ? (
          <label 
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`
              block w-full aspect-[21/9] rounded-3xl border-2 border-dashed transition-all duration-500 cursor-pointer
              flex flex-col items-center justify-center p-12 text-center
              ${dragActive ? 'bg-brand-cyan/20 border-brand-cyan scale-102' : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'}
            `}
          >
            <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6">
                <Upload className={`w-8 h-8 ${dragActive ? 'text-brand-cyan animate-bounce' : 'text-gray-400'}`} />
            </div>
            <h2 className="text-2xl font-bold mb-2">Drop your video here</h2>
            <p className="text-gray-500">or click to browse from your computer</p>
            <input type="file" className="hidden" accept="video/*" onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) { setFile(f); setPreview(URL.createObjectURL(f)); }
            }} />
          </label>
        ) : (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Preview & Success */}
            <div className="glass-panel rounded-3xl p-4 flex flex-col md:flex-row items-center gap-6 border-white/10">
              <div className="w-full md:w-64 aspect-video rounded-2xl bg-black overflow-hidden relative border border-white/5">
                <video src={preview!} className="w-full h-full object-cover opacity-60" />
                <button 
                  onClick={() => { setFile(null); setPreview(null); }}
                  className="absolute top-2 right-2 p-1.5 bg-black/60 rounded-full text-white hover:text-red-400 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="flex-1 text-center md:text-left">
                <h3 className="text-xl font-bold mb-1">{file.name}</h3>
                <p className="text-gray-400 text-sm">{(file.size / 1024 / 1024).toFixed(1)} MB • High Quality Detected</p>
                <div className="mt-4 flex items-center gap-2 text-emerald-400 text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Footage ready for the Hollywood Pipeline</span>
                </div>
              </div>
            </div>

            {/* Vibe Selection */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {VIBES.map((v) => (
                <button
                  key={v.id}
                  onClick={() => setSelectedVibe(v)}
                  className={`
                    p-6 rounded-3xl border text-left transition-all duration-300 relative overflow-hidden group
                    ${selectedVibe.id === v.id 
                      ? 'bg-white/10 border-white/40 ring-2 ring-white/10' 
                      : 'bg-white/5 border-white/5 hover:border-white/20 hover:bg-white/10'}
                  `}
                >
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 bg-white/5 ${selectedVibe.id === v.id ? 'scale-110' : ''} transition-transform`}>
                    {v.icon}
                  </div>
                  <h4 className="font-bold text-lg mb-1">{v.label}</h4>
                  <p className="text-xs text-gray-500 leading-relaxed">{v.description}</p>
                  
                  {selectedVibe.id === v.id && (
                    <div className="absolute top-4 right-4 animate-in zoom-in duration-300">
                      <CheckCircle2 className="w-5 h-5 text-brand-cyan" />
                    </div>
                  )}
                </button>
              ))}
            </div>

            {/* Final Action */}
            <div className="pt-6">
              {error && (
                <div className="mb-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  {error}
                </div>
              )}
              
              <button
                onClick={handleGo}
                disabled={uploading}
                className="w-full py-6 rounded-3xl bg-gradient-to-r from-brand-cyan via-brand-violet to-brand-fuchsia text-black font-black text-xl tracking-tight shadow-[0_0_50px_rgba(6,182,212,0.3)] hover:shadow-[0_0_70px_rgba(6,182,212,0.5)] transition-all disabled:opacity-50 disabled:scale-100 active:scale-95 group relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                <span className="relative z-10 flex items-center justify-center gap-3">
                  {uploading ? (
                    <>
                      <div className="w-6 h-6 border-4 border-black/20 border-t-black rounded-full animate-spin" />
                      <span>{progress < 90 ? `Processing Your Magic... ${progress}%` : 'Finalizing...'}</span>
                    </>
                  ) : (
                    <>
                      <span>CREATE MY VIDEO</span>
                      <Sparkles className="w-6 h-6 animate-pulse" />
                    </>
                  )}
                </span>
              </button>
              <p className="text-center text-gray-500 text-xs mt-4">
                By clicking, you use 1 credit. Our experts will handle everything in 2-5 minutes.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Stats/Social Proof */}
      {!file && (
        <div className="mt-20 flex flex-wrap justify-center gap-12 opacity-40 grayscale hover:grayscale-0 transition-all duration-500">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            <span className="font-bold tracking-widest text-xs uppercase">Hollywood Agents</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            <span className="font-bold tracking-widest text-xs uppercase">Instant Color Grade</span>
          </div>
          <div className="flex items-center gap-2">
            <Video className="w-5 h-5" />
            <span className="font-bold tracking-widest text-xs uppercase">Auto QC Polish</span>
          </div>
        </div>
      )}
    </div>
  );
}
