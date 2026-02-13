'use client';
import { useState, useCallback, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, X, Film, Zap, Layers, Monitor, Shield, Sparkles, CheckCircle2, Loader2, ArrowRight, Activity, BrainCircuit } from 'lucide-react';
import { apiUpload, apiRequest, ApiError, clearAuth } from '@/lib/api';
import { ffmpegAnalyzer, MediaIntelligence } from '@/lib/ffmpeg-analyzer';
import { Button } from '@/components/ui/Button';

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
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<MediaIntelligence | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    console.log('[UploadPage] Mounting...');
    setMounted(true);
    return () => console.log('[UploadPage] Unmounting...');
  }, []);

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
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      processNewFile(droppedFile);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      processNewFile(selected);
    }
  };

  const processNewFile = (newFile: File) => {
    setFile(newFile);
    setPreview(URL.createObjectURL(newFile));
    // Safe UUID generation for non-secure contexts
    const uuid = (typeof crypto !== 'undefined' && crypto.randomUUID)
      ? crypto.randomUUID()
      : `job_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
    setIdempotencyKey(uuid);
    setJobId(null);
    setStarting(false);
    setUploadProgress(0);
    setAnalysisResult(null);
    runAnalysis(newFile);
  };

  const runAnalysis = async (videoFile: File) => {
    setAnalyzing(true);
    setAnalysisProgress(0);
    try {
      // Lazy load FFmpeg only when needed
      await ffmpegAnalyzer.load().catch(e => console.error("FFmpeg load fail:", e));
      const result = await ffmpegAnalyzer.analyze(videoFile, (p) => setAnalysisProgress(p));
      setAnalysisResult(result);
    } catch (err) {
      console.error('Analysis failed:', err);
      // Fallback: Don't block upload if analysis fails
      setAnalyzing(false);
    } finally {
      setAnalyzing(false);
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

      if (analysisResult) {
        formData.append('media_intelligence', JSON.stringify(analysisResult));
      }

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
    } catch (err: any) {
      if (err instanceof ApiError && err.isAuth) {
        clearAuth();
        router.push('/login');
        return;
      }
      setError(err instanceof ApiError ? err.message : 'Upload failed');
      setUploading(false);
    }
  };

  const handleStartEdit = async () => {
    if (!jobId) return;
    setStarting(true);
    setError('');
    try {
      await apiRequest(`/jobs/${jobId}/start`, { method: 'POST', auth: true });
      router.push(`/dashboard`);
    } catch (err: any) {
      setError(err instanceof ApiError ? err.message : 'Failed to start pipeline');
      setStarting(false);
    }
  };

  if (!mounted) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4 animate-pulse">
        <div className="w-16 h-16 rounded-3xl bg-white/5 border border-white/10" />
        <div className="h-4 w-32 bg-white/5 rounded-full" />
        <div className="h-2 w-48 bg-white/5 rounded-full opacity-50" />
      </div>
    );
  }

  return (
    <div className="flex flex-col xl:flex-row gap-8 xl:gap-12 min-h-[calc(100vh-14rem)] pb-20 px-2 md:px-0">
      {/* Project Intelligence - Side Panel */}
      <div className="w-full xl:w-[420px] flex-shrink-0 flex flex-col gap-8">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="px-3 py-1 rounded-full bg-brand-cyan/10 border border-brand-cyan/30 text-[10px] font-black uppercase tracking-widest text-brand-cyan">ENGINE_CFG</div>
            <span className="text-[10px] font-bold text-gray-600 uppercase tracking-widest">Build v4.0.2</span>
          </div>
          <h1 className="text-4xl font-black tracking-tighter text-white uppercase">Project Node</h1>
          <p className="text-gray-500 font-bold text-sm tracking-tight">Configure legislative parameters for the Hollywood Pipeline.</p>
        </div>

        <div className="glass-panel p-8 rounded-[40px] border-white/5 space-y-10 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-brand-cyan/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

          {/* Pipeline Selector */}
          <div className="space-y-4">
            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 ml-1">Computation Tier</label>
            <div className="bg-white/5 rounded-[24px] p-1.5 flex relative border border-white/5">
              <div className={`absolute inset-y-1.5 w-[calc(50%-6px)] bg-brand-cyan/20 rounded-2xl transition-all duration-500 ${settings.premium ? 'translate-x-full' : 'translate-x-0'}`} />
              <button
                onClick={() => setSettings(s => ({ ...s, premium: false }))}
                className={`flex-1 flex items-center justify-center gap-3 py-4 rounded-2xl relative z-10 transition-all ${!settings.premium ? 'text-brand-cyan' : 'text-gray-600 hover:text-gray-400'}`}
              >
                <Zap className="w-4 h-4" />
                <span className="text-[10px] font-black uppercase tracking-widest">Standard</span>
              </button>
              <button
                onClick={() => setSettings(s => ({ ...s, premium: true }))}
                className={`flex-1 flex items-center justify-center gap-3 py-4 rounded-2xl relative z-10 transition-all ${settings.premium ? 'text-brand-cyan' : 'text-gray-600 hover:text-gray-400'}`}
              >
                <Sparkles className="w-4 h-4" />
                <span className="text-[10px] font-black uppercase tracking-widest">Pro Studio</span>
              </button>
            </div>
            {settings.premium && (
              <p className="text-[10px] font-bold text-cyan-500 uppercase tracking-widest text-center animate-pulse mt-2">Extended Sub-Agent Intelligence Active</p>
            )}
          </div>

          {/* Target Platform */}
          <div className="space-y-4">
            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 ml-1">Deployment Node</label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: 'youtube', label: 'YouTube', icon: Monitor },
                { id: 'tiktok', label: 'TikTok', icon: Film },
                { id: 'instagram', label: 'Instagram', icon: Layers },
                { id: 'linkedin', label: 'LinkedIn', icon: Shield }
              ].map(p => (
                <button
                  key={p.id}
                  onClick={() => setSettings(s => ({ ...s, platform: p.id }))}
                  className={`flex items-center gap-3 px-4 py-4 rounded-[20px] border transition-all duration-500 ${settings.platform === p.id
                    ? 'bg-brand-cyan/10 border-brand-cyan/30 text-white shadow-xl shadow-brand-cyan/5 scale-[1.02]'
                    : 'bg-white/5 border-transparent text-gray-600 hover:bg-white/10 hover:text-gray-400'
                    }`}
                >
                  <p.icon className="w-4 h-4" />
                  <span className="text-[10px] font-black uppercase tracking-widest">{p.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Creative Style */}
          <div className="space-y-4">
            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 ml-1">Narrative Engine</label>
            <div className="grid grid-cols-2 gap-3">
              {['Cinematic', 'Energetic', 'Minimal', 'Modern'].map(style => (
                <button
                  key={style}
                  onClick={() => setSettings(s => ({ ...s, theme: style.toLowerCase() }))}
                  className={`px-4 py-4 rounded-[20px] border text-[10px] font-black uppercase tracking-widest transition-all duration-500 ${settings.theme === style.toLowerCase()
                    ? 'bg-white text-black border-white shadow-xl scale-[1.02]'
                    : 'bg-white/5 border-transparent text-gray-600 hover:bg-white/10 hover:text-gray-400'
                    }`}
                >
                  {style}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-black uppercase tracking-widest text-center">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Immersive Drop Zone - Main Area */}
      <div className="flex-1 min-h-[500px] xl:min-h-0 rounded-[48px] overflow-hidden relative glass-panel group border-white/5 bg-obsidian-900/30">
        <div className="absolute inset-0 bg-grid-pattern opacity-5" />

        {dragActive && (
          <div className="absolute inset-0 bg-brand-cyan/10 backdrop-blur-md z-20 border-2 border-brand-cyan border-dashed rounded-[48px] m-6 animate-pulse" />
        )}

        <div className="relative z-10 w-full h-full flex flex-col">
          {preview ? (
            <div className="flex-1 flex flex-col h-full">
              <div className="flex-1 relative flex items-center justify-center p-8 bg-black/40">
                <video src={preview} className="max-w-full max-h-full rounded-[32px] shadow-[0_40px_100px_rgba(0,0,0,0.8)] border border-white/5" controls />
                <button
                  onClick={() => { setFile(null); setPreview(null); setJobId(null); }}
                  className="absolute top-8 right-8 p-3 bg-black/60 hover:bg-black text-white rounded-full backdrop-blur-2xl transition-all border border-white/10 group/close"
                >
                  <X className="w-6 h-6 group-hover:rotate-90 transition-transform" />
                </button>
              </div>

              <div className="p-10 bg-gradient-to-t from-obsidian-950 via-obsidian-950 to-transparent">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 mb-10">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <BrainCircuit className="w-4 h-4 text-brand-cyan" />
                      <span className="text-[10px] font-black uppercase tracking-[0.3em] text-brand-cyan">TELEMETRY_SYNC_INITIATED</span>
                    </div>
                    <h3 className="text-3xl font-black text-white truncate max-w-2xl tracking-tight">{file?.name}</h3>
                    <p className="text-[10px] font-bold text-gray-600 uppercase tracking-[0.2em]">
                      {(file?.size ? (file.size / 1024 / 1024).toFixed(2) : 0)} MB • {(analyzing ? "ANALYZING_BEATS..." : "MEDIA_READY")}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    <Button
                      onClick={handleUpload}
                      disabled={uploading || !!jobId || analyzing}
                      variant={jobId ? "secondary" : "glow"}
                      className="w-full md:w-auto h-16 px-12 font-black text-xs uppercase tracking-[0.3em]"
                      loading={uploading || analyzing}
                    >
                      {jobId ? (
                        <><CheckCircle2 className="w-5 h-5 mr-3" /> UPLOADED</>
                      ) : (
                        <><Sparkles className="w-5 h-5 mr-3" /> {analyzing ? `ANALYZING ${analysisProgress}%` : `START UPLOAD`}</>
                      )}
                    </Button>
                  </div>
                </div>

                {(uploading || uploadProgress > 0) && (
                  <div className="space-y-3 animate-in fade-in duration-700">
                    <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-brand-cyan to-brand-violet shadow-[0_0_15px_rgba(6,182,212,0.8)] transition-all duration-300" style={{ width: `${uploadProgress}%` }} />
                    </div>
                    <div className="flex justify-between text-[10px] font-black text-gray-600 uppercase tracking-[0.4em]">
                      <span>Transferring Assets</span>
                      <span className="text-brand-cyan">{uploadProgress}%</span>
                    </div>
                  </div>
                )}

                {jobId && (
                  <div className="mt-8 flex flex-col md:flex-row items-center gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <div className="flex-1 flex items-center gap-4 px-6 py-4 bg-emerald-400/5 border border-emerald-400/20 rounded-[24px]">
                      <Activity className="w-5 h-5 text-emerald-400 animate-pulse" />
                      <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Job Enqueued: Node #{jobId} Verified</span>
                    </div>
                    <Button onClick={handleStartEdit} variant="primary" className="w-full md:w-auto h-16 px-12 group font-black text-xs uppercase tracking-[0.3em]" loading={starting}>
                      START EDITING
                      <ArrowRight className="w-5 h-5 ml-4 group-hover:translate-x-2 transition-transform" />
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <label className="flex-1 flex flex-col items-center justify-center cursor-pointer p-12 hover:bg-white/[0.01] transition-all duration-700 group/drop">
              <div className="w-32 h-32 md:w-48 md:h-48 rounded-[64px] bg-white/[0.02] border border-white/5 flex items-center justify-center mb-10 relative transition-all duration-700 group-hover/drop:scale-110 group-hover/drop:rotate-6 group-hover/drop:border-brand-cyan/30">
                <div className="absolute inset-0 bg-gradient-to-tr from-brand-cyan/20 to-brand-violet/20 rounded-[64px] blur-3xl opacity-0 group-hover/drop:opacity-100 transition-opacity duration-1000" />
                <Upload className="w-12 h-12 md:w-16 md:h-16 text-gray-700 transition-all duration-700 group-hover/drop:text-brand-cyan group-hover/drop:scale-110" />
              </div>
              <h2 className="text-3xl md:text-5xl font-black text-white mb-4 text-center tracking-tighter uppercase">Deploy Footage</h2>
              <p className="text-gray-500 text-center text-xs md:text-sm font-bold uppercase tracking-[0.3em] max-w-sm mb-12 leading-relaxed">
                RAW_ASSETS: MP4, MOV, AVI <br />
                <span className="text-brand-cyan">BANDWIDTH_LIMIT: 100MB</span>
              </p>
              <div className="px-12 py-6 rounded-[24px] bg-white text-black font-black text-sm uppercase tracking-[0.3em] shadow-[0_0_30px_rgba(255,255,255,0.3)] hover:scale-105 active:scale-95 transition-all">
                SELECT VIDEO FILE
              </div>
              <input
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
            </label>
          )}
        </div>
      </div>
    </div>
  );
}
