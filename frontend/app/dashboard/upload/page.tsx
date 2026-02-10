'use client';
import { useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, X, Film, Zap, Layers, Monitor, Shield, Sparkles } from 'lucide-react';
import { apiUpload, apiRequest, ApiError, clearAuth } from '@/lib/api';

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const uploadAbortRef = useRef<null | (() => void)>(null);
  const [idempotencyKey, setIdempotencyKey] = useState<string | null>(null);
  const [jobId, setJobId] = useState<number | null>(null);
  const [starting, setStarting] = useState(false);

  const [settings, setSettings] = useState({
    theme: 'cinematic',
    pacing: 'medium',
    mood: 'professional',
    ratio: '16:9',
    platform: 'youtube',
    premium: true,
    brandSafety: 'standard'
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      setFile(droppedFile);
      setPreview(URL.createObjectURL(droppedFile));
      setIdempotencyKey(typeof crypto !== 'undefined' ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`);
      setJobId(null);
      setStarting(false);
      setUploadProgress(0);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setIdempotencyKey(typeof crypto !== 'undefined' ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`);
      setJobId(null);
      setStarting(false);
      setUploadProgress(0);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);
    setError('');

    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      setUploading(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('theme', settings.theme);
      formData.append('pacing', settings.pacing);
      formData.append('mood', settings.mood);
      formData.append('ratio', settings.ratio);
      formData.append('platform', settings.platform);
      formData.append('tier', settings.premium ? 'pro' : 'standard');
      formData.append('brand_safety', settings.brandSafety);

      const { promise, abort } = apiUpload<{ id: number }>('/jobs/upload', {
        body: formData,
        auth: true,
        headers: idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : undefined,
        onProgress: setUploadProgress,
      });
      uploadAbortRef.current = abort;
      const job = await promise;
      setJobId(job.id);
      setUploading(false);
      setUploadProgress(100);
      uploadAbortRef.current = null;
    } catch (err: any) {
      if (err instanceof ApiError && err.isAuth) {
        clearAuth();
        router.push('/login');
        return;
      }
      setError(err instanceof ApiError ? err.message : 'Upload failed');
      setUploading(false);
      uploadAbortRef.current = null;
    }
  };

  const handleStartEdit = async () => {
    if (!jobId) return;
    setStarting(true);
    setError('');
    try {
      await apiRequest(`/jobs/${jobId}/start`, { method: 'POST', auth: true });
      router.push(`/jobs/${jobId}`);
    } catch (err: any) {
      setError(err instanceof ApiError ? err.message : 'Failed to start pipeline');
      setStarting(false);
    }
  };

  const handleCancelUpload = () => {
    if (uploadAbortRef.current) {
      uploadAbortRef.current();
      uploadAbortRef.current = null;
    }
    setUploading(false);
    setUploadProgress(0);
    setError('Upload canceled.');
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-8">
      {/* Left Column: Configuration Wizard */}
      <div className="w-[450px] flex-shrink-0 flex flex-col gap-6 overflow-y-auto custom-scrollbar pr-2">

        <div className="space-y-2">
          <h1 className="text-3xl font-display font-bold">New Project</h1>
          <p className="text-gray-400">Configure your creative vision.</p>
        </div>

        {/* Settings Panel */}
        <div className="space-y-8 glass-panel p-6 rounded-2xl">

          {/* Pipeline Selector */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-300">Processing Pipeline</label>
            <div className="bg-obsidian-900 rounded-xl p-1 flex relative">
              <div className={`absolute inset-y-1 w-1/2 bg-white/10 rounded-lg transition-all duration-300 ${settings.premium ? 'translate-x-full left-[-4px]' : 'left-1'}`} />
              <button
                onClick={() => setSettings(s => ({ ...s, premium: false }))}
                className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg relative z-10 transition-colors ${!settings.premium ? 'text-white' : 'text-gray-500 hover:text-gray-300'}`}
              >
                <Zap className="w-4 h-4" />
                <span className="font-medium">Standard</span>
              </button>
              <button
                onClick={() => setSettings(s => ({ ...s, premium: true }))}
                className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg relative z-10 transition-colors ${settings.premium ? 'text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
              >
                <Sparkles className={`w-4 h-4 ${settings.premium ? 'text-brand-cyan' : ''}`} />
                <span className={`font-medium ${settings.premium ? 'gradient-text bg-gradient-to-r from-brand-cyan to-brand-violet' : ''}`}>Pro Studio</span>
              </button>
            </div>
            <p className="text-xs text-gray-500 px-1">
              {settings.premium
                ? "Includes: Multi-Agent Director, Deep Media Intelligence, & Hybrid Memory."
                : "Basic automated editing sequence."}
            </p>
          </div>

          {/* Platform */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-300">Target Platform</label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: 'youtube', label: 'YouTube', icon: <Monitor className="w-4 h-4" /> },
                { id: 'tiktok', label: 'TikTok', icon: <Film className="w-4 h-4" /> },
                { id: 'instagram', label: 'Instagram', icon: <Layers className="w-4 h-4" /> },
                { id: 'linkedin', label: 'LinkedIn', icon: <Shield className="w-4 h-4" /> }
              ].map(p => (
                <button
                  key={p.id}
                  onClick={() => setSettings(s => ({ ...s, platform: p.id }))}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-200 text-left ${settings.platform === p.id
                      ? 'bg-brand-cyan/10 border-brand-cyan text-white shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                      : 'bg-white/5 border-transparent text-gray-400 hover:bg-white/10 hover:text-white'
                    }`}
                >
                  {p.icon}
                  <span className="text-sm font-medium">{p.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Style & Mood */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-300">Creative Direction</label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: 'cinematic', label: 'Cinematic' },
                { id: 'energetic', label: 'High Energy' },
                { id: 'minimal', label: 'Minimalist' },
                { id: 'documentary', label: 'Docu-Style' },
              ].map(theme => (
                <button
                  key={theme.id}
                  onClick={() => setSettings(s => ({ ...s, theme: theme.id }))}
                  className={`px-4 py-3 rounded-xl border text-sm font-medium transition-all ${settings.theme === theme.id
                      ? 'bg-white text-black border-white'
                      : 'bg-black/40 border-white/10 text-gray-400 hover:border-white/30'
                    }`}
                >
                  {theme.label}
                </button>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3">
              <Shield className="w-5 h-5 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}
        </div>
      </div>

      {/* Right Column: Immersive Drop Zone */}
      <div className="flex-1 rounded-3xl overflow-hidden relative group">
        {/* Dynamic Background */}
        <div className="absolute inset-0 bg-obsidian-900">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-brand-violet/5 rounded-full blur-[120px] animate-pulse-slow" />
          {dragActive && (
            <div className="absolute inset-0 bg-brand-cyan/10 backdrop-blur-sm z-20 transition-all duration-300 border-4 border-brand-cyan border-dashed rounded-3xl m-4" />
          )}
        </div>

        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className="relative z-10 w-full h-full flex flex-col"
        >
          {preview ? (
            <div className="relative w-full h-full bg-black flex items-center justify-center">
              <video src={preview} className="max-w-full max-h-full" controls />

              {/* Overlay Controls */}
              <div className="absolute top-6 right-6 flex gap-3">
                <button
                  onClick={() => { setFile(null); setPreview(null); setIdempotencyKey(null); setJobId(null); setUploadProgress(0); }}
                  className="p-3 bg-black/60 hover:bg-red-500/20 text-white hover:text-red-400 rounded-full backdrop-blur-md transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="absolute bottom-0 left-0 right-0 p-8 bg-gradient-to-t from-black/90 to-transparent">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-white mb-1">{file?.name}</h3>
                    <p className="text-sm text-gray-400">{(file?.size ? (file.size / 1024 / 1024).toFixed(2) : 0)} MB - Ready for Analysis</p>
                  </div>
                  <button
                    onClick={handleUpload}
                    disabled={uploading || !!jobId}
                    className="px-8 py-4 bg-brand-cyan hover:bg-brand-accent text-black font-bold rounded-xl transition-all hover:scale-105 disabled:opacity-50 disabled:scale-100 flex items-center gap-3 shadow-[0_0_20px_rgba(6,182,212,0.4)]"
                  >
                    {uploading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                        <span>Uploading {uploadProgress}%</span>
                      </>
                    ) : jobId ? (
                      <>
                        <Sparkles className="w-5 h-5" />
                        <span>Upload Complete</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5" />
                        <span>Upload Video</span>
                      </>
                    )}
                  </button>
                  {jobId && (
                    <button
                      onClick={handleStartEdit}
                      disabled={starting}
                      className="px-6 py-4 bg-white/5 hover:bg-white/10 text-white font-semibold rounded-xl transition-colors disabled:opacity-60"
                    >
                      {starting ? 'Starting...' : 'Start Edit'}
                    </button>
                  )}
                  {uploading && (
                    <button
                      onClick={handleCancelUpload}
                      className="px-6 py-4 bg-white/5 hover:bg-white/10 text-white font-semibold rounded-xl transition-colors"
                    >
                      Cancel
                    </button>
                  )}
                </div>
                {uploading && (
                  <div className="mt-4">
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-brand-cyan transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-2">Uploading your video. Don&apos;t close this tab.</p>
                  </div>
                )}
                {jobId && !uploading && (
                  <p className="text-xs text-gray-400 mt-3">
                    Upload complete. Click <span className="text-white font-semibold">Start Edit</span> to begin processing.
                  </p>
                )}
              </div>
            </div>
          ) : (
            <label className="flex-1 flex flex-col items-center justify-center cursor-pointer p-12 hover:bg-white/5 transition-colors duration-300 group/drop">
              <div className="w-32 h-32 rounded-full bg-white/5 flex items-center justify-center mb-8 relative group-hover/drop:scale-110 transition-transform duration-500">
                <div className="absolute inset-0 bg-gradient-to-tr from-brand-cyan/20 to-brand-violet/20 rounded-full animate-spin-slow opacity-50" />
                <Upload className="w-12 h-12 text-gray-400 group-hover/drop:text-white transition-colors" />
              </div>
              <h2 className="text-3xl font-bold text-white mb-2 text-center">Drag & Drop Footage</h2>
              <p className="text-gray-400 text-center max-w-sm mb-8">
                Support for MP4, MOV, and AVI up to 100MB. <br />
                <span className="text-brand-cyan">Pro Tip:</span> Upload raw footage for best results.
              </p>
              <span className="px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-medium transition-colors">
                Browse Files
              </span>
              <input type="file" accept="video/*" onChange={handleFileChange} className="hidden" />
            </label>
          )}
        </div>
      </div>
    </div>
  );
}
