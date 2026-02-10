'use client';
import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, Sparkles, Zap, Video, CheckCircle2, X, BrainCircuit, ScanSearch, Layers } from 'lucide-react';
import { apiUpload, apiRequest, ApiError, clearAuth } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { motion, AnimatePresence } from 'framer-motion';

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
  const [isScanning, setIsScanning] = useState(false);
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
      setIsScanning(true);
      setTimeout(() => setIsScanning(false), 2000);
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
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-6xl font-bold mb-4 tracking-tight">
            Drop it. <span className="bg-gradient-to-r from-brand-cyan to-brand-violet bg-clip-text text-transparent">Vibe it.</span> Done.
          </h1>
          <p className="text-gray-400 text-lg">The world&apos;s simplest editor. No timelines, just results.</p>
        </motion.div>

        <AnimatePresence mode="wait">
          {!file ? (
            <motion.label
              key="dropzone"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`
                block w-full aspect-[21/9] rounded-3xl border-2 border-dashed transition-all duration-500 cursor-pointer
                flex flex-col items-center justify-center p-12 text-center relative overflow-hidden group
                ${dragActive ? 'bg-brand-cyan/20 border-brand-cyan' : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'}
              `}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-brand-cyan/5 via-transparent to-brand-violet/5 opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6 relative z-10 transition-transform group-hover:scale-110">
                <Upload className={`w-8 h-8 ${dragActive ? 'text-brand-cyan animate-bounce' : 'text-gray-400 group-hover:text-brand-cyan'}`} />
              </div>
              <h2 className="text-2xl font-bold mb-2 relative z-10">Drop your video here</h2>
              <p className="text-gray-500 relative z-10">or click to browse from your computer</p>
              <input type="file" className="hidden" accept="video/*" onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) {
                  setFile(f);
                  setPreview(URL.createObjectURL(f));
                  setIsScanning(true);
                  setTimeout(() => setIsScanning(false), 2000);
                }
              }} />
            </motion.label>
          ) : isScanning ? (
            <motion.div
              key="scanning"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="glass-panel border-brand-cyan/20 rounded-3xl p-20 flex flex-col items-center justify-center gap-6"
            >
              <div className="relative">
                <BrainCircuit className="w-16 h-16 text-brand-cyan animate-pulse" />
                <div className="absolute inset-0 bg-brand-cyan/20 blur-2xl animate-pulse" />
              </div>
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-2">Analyzing Footage</h3>
                <p className="text-gray-500">Engaging Hollywood Agents to map visual beats...</p>
              </div>
              <div className="w-64 h-1 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 2, ease: "easeInOut" }}
                  className="h-full bg-brand-cyan"
                />
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="editor"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-8"
            >
              {/* Preview & Success */}
              <div className="glass-panel rounded-3xl p-4 flex flex-col md:flex-row items-center gap-6 border-white/10 group">
                <div className="w-full md:w-64 aspect-video rounded-2xl bg-black overflow-hidden relative border border-white/5 shadow-2xl shadow-black/50">
                  <video src={preview!} className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                  <button
                    onClick={() => { setFile(null); setPreview(null); }}
                    className="absolute top-2 right-2 p-1.5 bg-black/60 rounded-full text-white hover:text-red-400 transition-colors backdrop-blur-md"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex-1 text-center md:text-left">
                  <div className="flex items-center gap-2 mb-1 justify-center md:justify-start">
                    <ScanSearch className="w-4 h-4 text-brand-cyan" />
                    <span className="text-[10px] font-bold uppercase tracking-widest text-brand-cyan">AI Analysis Complete</span>
                  </div>
                  <h3 className="text-xl font-bold mb-1 truncate max-w-sm">{file.name}</h3>
                  <p className="text-gray-400 text-sm">{(file.size / 1024 / 1024).toFixed(1)} MB • 4K Bitrate detected</p>
                  <div className="mt-4 flex items-center gap-2 text-emerald-400 text-sm justify-center md:justify-start">
                    <CheckCircle2 className="w-4 h-4" />
                    <span className="font-medium">Ready for the Hollywood Pipeline</span>
                  </div>
                </div>
              </div>

              {/* Vibe Selection Header */}
              <div className="flex items-center gap-3 px-2">
                <Layers className="w-5 h-5 text-brand-violet" />
                <h3 className="text-lg font-bold">Choose your Vibe</h3>
              </div>

              {/* Vibe Selection */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {VIBES.map((v) => (
                  <button
                    key={v.id}
                    onClick={() => setSelectedVibe(v)}
                    className={`
                      p-6 rounded-3xl border text-left transition-all duration-500 relative overflow-hidden group
                      ${selectedVibe.id === v.id
                        ? 'bg-white/10 border-brand-cyan/50 shadow-2xl shadow-brand-cyan/5'
                        : 'bg-white/5 border-white/5 hover:border-white/20 hover:bg-white/10'}
                    `}
                  >
                    {selectedVibe.id === v.id && (
                      <motion.div
                        layoutId="vibe-bg"
                        className="absolute inset-0 bg-gradient-to-br from-brand-cyan/10 via-brand-violet/5 to-transparent"
                      />
                    )}

                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 bg-white/5 relative z-10 transition-transform duration-500 ${selectedVibe.id === v.id ? 'scale-110 bg-brand-cyan/10' : ''}`}>
                      {v.icon}
                    </div>
                    <h4 className="font-bold text-lg mb-1 relative z-10">{v.label}</h4>
                    <p className="text-xs text-gray-500 leading-relaxed relative z-10">{v.description}</p>

                    {selectedVibe.id === v.id && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="absolute top-4 right-4 z-10"
                      >
                        <CheckCircle2 className="w-5 h-5 text-brand-cyan" />
                      </motion.div>
                    )}
                  </button>
                ))}
              </div>

              {/* Final Action */}
              <div className="pt-6">
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                  >
                    {error}
                  </motion.div>
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
                <div className="flex items-center justify-center gap-4 mt-6">
                  <div className="h-px bg-white/5 flex-1" />
                  <p className="text-gray-500 text-[10px] font-bold uppercase tracking-widest whitespace-nowrap">
                    1 Credit • Est. Time 2-5m
                  </p>
                  <div className="h-px bg-white/5 flex-1" />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
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
