'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import MediaStats from '@/components/dashboard/MediaStats';
import QCScoreBoard from '@/components/dashboard/QCScoreBoard';
import { ArrowLeft, Download, RotateCcw, Share2, MoreHorizontal, Film, Activity, CheckCircle2, AlertCircle, Sparkles, Zap, Shield, Clock, ExternalLink } from 'lucide-react';

import BrandSafetyCard from '@/components/dashboard/BrandSafetyCard';
import ABTestVariants from '@/components/dashboard/ABTestVariants';
import { apiRequest, ApiError, clearAuth, API_ORIGIN, getWebSocketUrl } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Job } from '@/lib/types';

export default function JobPageClient({ id }: { id: string }) {
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState('');
  const socketRef = useRef<WebSocket | null>(null);
  const [actionError, setActionError] = useState('');
  const [showEdit, setShowEdit] = useState(false);
  const [editError, setEditError] = useState('');
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [editForm, setEditForm] = useState({
    theme: 'professional',
    pacing: 'medium',
    mood: 'professional',
    ratio: '16:9',
    platform: 'youtube',
    tier: 'pro',
    brand_safety: 'standard',
    transition_style: 'dissolve',
    transition_duration: 0.25,
    speed_profile: 'balanced',
    subtitle_preset: 'platform_default',
    color_profile: 'natural',
    skin_protect_strength: 0.5,
  });

  const fetchJob = useCallback(async () => {
    try {
      const data = await apiRequest<Job>(`/jobs/${id}`, { auth: true });
      setJob(data);
    } catch (err: any) {
      if (err instanceof ApiError && err.isAuth) {
        clearAuth();
        router.push('/login');
        return;
      }
      setError(err instanceof ApiError ? err.message : 'Job not found');
    }
  }, [id, router]);

  const handleCancel = async () => {
    if (!job) return;
    setActionError('');
    try {
      await apiRequest(`/jobs/${job.id}/cancel`, { method: 'POST', auth: true });
      fetchJob();
    } catch (err: any) {
      setActionError(err instanceof ApiError ? err.message : 'Failed to cancel job');
    }
  };

  const handleRetry = async () => {
    if (!job) return;
    setActionError('');
    try {
      await apiRequest(`/jobs/${job.id}/retry`, { method: 'POST', auth: true });
      fetchJob();
    } catch (err: any) {
      setActionError(err instanceof ApiError ? err.message : 'Failed to retry job');
    }
  };

  const handleStart = async () => {
    if (!job) return;
    setActionError('');
    try {
      await apiRequest(`/jobs/${job.id}/start`, { method: 'POST', auth: true });
      fetchJob();
    } catch (err: any) {
      setActionError(err instanceof ApiError ? err.message : 'Failed to start job');
    }
  };

  const openEdit = () => {
    if (!job) return;
    setEditForm({
      theme: job.theme || 'professional',
      pacing: job.pacing || 'medium',
      mood: job.mood || 'professional',
      ratio: job.ratio || '16:9',
      platform: job.platform || 'youtube',
      tier: job.tier || 'pro',
      brand_safety: job.brand_safety || 'standard',
      transition_style: job.post_settings?.transition_style || 'dissolve',
      transition_duration: Number(job.post_settings?.transition_duration ?? 0.25),
      speed_profile: job.post_settings?.speed_profile || 'balanced',
      subtitle_preset: job.post_settings?.subtitle_preset || 'platform_default',
      color_profile: job.post_settings?.color_profile || 'natural',
      skin_protect_strength: Number(job.post_settings?.skin_protect_strength ?? 0.5),
    });
    setEditError('');
    setShowEdit(true);
  };

  const submitEdit = async () => {
    if (!job) return;
    setEditSubmitting(true);
    setEditError('');
    try {
      const idempotencyKey = typeof crypto !== 'undefined' ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
      const created = await apiRequest<{ id: number }>(`/jobs/${job.id}/edit`, {
        method: 'POST',
        auth: true,
        body: editForm,
        headers: { 'Idempotency-Key': idempotencyKey },
      });
      setShowEdit(false);
      router.push(`/jobs/${created.id}`);
    } catch (err: any) {
      setEditError(err instanceof ApiError ? err.message : 'Failed to create edit');
    } finally {
      setEditSubmitting(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    fetchJob();
    const interval = setInterval(fetchJob, 10000);
    return () => clearInterval(interval);
  }, [fetchJob, router]);

  useEffect(() => {
    if (!id) return;
    const ws = new WebSocket(getWebSocketUrl(`/ws/jobs/${id}`));
    socketRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        setJob((prev) =>
          prev ? { ...prev, status: payload.status ?? prev.status, progress_message: payload.message ?? prev.progress_message } : prev
        );
        if (payload.status === 'complete' || payload.status === 'failed') {
          fetchJob();
        }
      } catch { /* ignore */ }
    };

    return () => ws.close();
  }, [fetchJob, id]);

  const stages = [
    { key: 'intel', label: 'Intelligence', icon: Activity },
    { key: 'director', label: 'Strategy', icon: Film },
    { key: 'platform', label: 'Adaptation', icon: Share2 },
    { key: 'render', label: 'Rendering', icon: Download },
    { key: 'qc', label: 'QC & Eval', icon: CheckCircle2 },
  ];

  const getCurrentStage = (message: string) => {
    if (!message) return 0;
    const m = message.toLowerCase();
    if (m.includes('intel')) return 0;
    if (m.includes('director') || m.includes('strategy')) return 1;
    if (m.includes('platform') || m.includes('adapt') || m.includes('specialist')) return 2;
    if (m.includes('render') || m.includes('compiling')) return 3;
    if (m.includes('review') || m.includes('quality') || m.includes('qc')) return 4;
    if (m.includes('complete') || m.includes('ready')) return 5;
    return 0;
  };

  const currentStage = job ? getCurrentStage(job.progress_message) : 0;

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
        <div className="w-16 h-16 rounded-3xl bg-red-500/10 flex items-center justify-center text-red-500 mb-6 border border-red-500/20">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-black tracking-tight mb-2">Sync Interrupted</h2>
        <p className="text-gray-500 mb-8 max-w-sm">{error}</p>
        <Link href="/dashboard">
          <Button variant="secondary" size="lg">Return to Dashboard</Button>
        </Link>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-20 h-20 relative mb-8">
          <div className="absolute inset-0 border-4 border-white/5 rounded-3xl" />
          <div className="absolute inset-0 border-4 border-t-brand-cyan rounded-3xl animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-brand-cyan animate-pulse" />
          </div>
        </div>
        <p className="text-xs font-black uppercase tracking-[0.3em] text-gray-500 animate-pulse">Initializing Studio</p>
      </div>
    );
  }

  const isComplete = job.status === 'complete';
  const isFailed = job.status === 'failed';
  const isProcessing = job.status === 'processing';
  const isQueued = job.status === 'queued';
  const videoUrl = job.output_path ? (job.output_path.startsWith('http') ? job.output_path : `${API_ORIGIN}/${job.output_path}`) : null;
  const lastUpdated = job.updated_at ? new Date(job.updated_at) : new Date(job.created_at);

  return (
    <div className="max-w-[1600px] mx-auto space-y-6 md:space-y-8 pb-12">
      {/* Header Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <Link href="/dashboard" className="flex items-center gap-3 text-gray-500 hover:text-white transition-all group">
          <div className="p-2 rounded-xl bg-white/5 group-hover:bg-white/10 transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </div>
          <span className="text-xs font-black uppercase tracking-widest">Back to Projects</span>
        </Link>

        <div className="flex flex-wrap items-center gap-3">
          <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-brand-cyan animate-pulse' : isComplete ? 'bg-emerald-400' : 'bg-gray-600'}`} />
            <span className="text-[10px] font-black uppercase tracking-widest text-gray-300">#{job.id} • {job.status}</span>
          </div>

          {isProcessing && <Button variant="danger" size="sm" onClick={handleCancel}>Cancel Job</Button>}
          {isQueued && <Button variant="glow" size="sm" onClick={handleStart}>Start Pipeline</Button>}
          {isFailed && <Button variant="primary" size="sm" onClick={handleRetry}>Retry Execution</Button>}

          <Button variant="secondary" size="sm" onClick={openEdit}>Configure</Button>

          <button className="p-2.5 bg-white/5 hover:bg-white/10 rounded-xl transition-all text-gray-400 hover:text-white border border-white/5">
            <MoreHorizontal className="w-5 h-5" />
          </button>
        </div>
      </div>

      {actionError && (
        <div className="glass-panel border-red-500/20 bg-red-500/5 p-4 rounded-2xl flex items-center gap-3 mb-4">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-xs font-bold text-red-200">{actionError}</span>
        </div>
      )}

      {/* Main Stage Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6 md:space-y-8">
          {/* Cinematic Visualizer */}
          <div className="aspect-video bg-black rounded-[32px] overflow-hidden relative group border border-white/5 shadow-2xl">
            {videoUrl && isComplete ? (
              <video src={videoUrl} controls className="w-full h-full object-contain" />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center relative bg-obsidian-900 border-white/5 inset-0">
                <div className="absolute inset-0 bg-grid-white/5 opacity-20" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-brand-cyan/5 rounded-full blur-[120px] animate-pulse-slow" />

                <div className="relative z-10 text-center px-6">
                  <div className="w-24 h-24 mx-auto mb-8 relative">
                    <div className="absolute inset-0 border-[6px] border-white/5 rounded-full" />
                    <div className="absolute inset-0 border-[6px] border-t-brand-cyan rounded-full animate-spin transition-all duration-1000" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-black tracking-tighter text-white">{Math.round((currentStage / stages.length) * 100)}%</span>
                    </div>
                  </div>
                  <h3 className="text-2xl font-black text-white mb-3 tracking-tight transition-all duration-500">
                    {job.progress_message || 'Spinning up Agents...'}
                  </h3>
                  <div className="flex items-center justify-center gap-3 text-xs font-black uppercase tracking-[0.2em] text-brand-cyan/80">
                    <Zap className="w-4 h-4 fill-brand-cyan animate-pulse" />
                    <span>Agent: {stages[Math.min(currentStage, stages.length - 1)].label}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Pipeline Engine Overview */}
          <div className="glass-panel p-6 md:p-8 rounded-[32px] border-white/5 relative overflow-hidden">
            <div className="flex items-center justify-between mb-8">
              <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500">Pipeline Engine Progress</h4>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-brand-cyan rounded-full animate-pulse" />
                <span className="text-[10px] font-bold text-brand-cyan uppercase tracking-widest">Live Sync</span>
              </div>
            </div>

            <div className="flex items-center justify-between relative">
              {stages.map((stage, i) => {
                const isActive = i === currentStage;
                const isPast = i < currentStage;
                const Icon = stage.icon;
                return (
                  <div key={stage.key} className="flex flex-col items-center gap-4 relative z-10 flex-1 group">
                    <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-700 border ${isActive ? 'bg-brand-cyan text-black border-brand-cyan shadow-[0_0_30px_rgba(6,182,212,0.4)] scale-110' :
                        isPast ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30' :
                          'bg-white/5 text-gray-600 border-transparent group-hover:bg-white/10'
                      }`}>
                      {isPast ? <CheckCircle2 className="w-6 h-6 stroke-[3]" /> : <Icon className="w-5 h-5" />}
                    </div>
                    <span className={`text-[10px] font-black uppercase tracking-widest transition-colors duration-500 ${isActive ? 'text-white' : 'text-gray-500'}`}>
                      {stage.label}
                    </span>

                    {i < stages.length - 1 && (
                      <div className="absolute top-6 left-1/2 w-full h-[2px] -z-10 px-6">
                        <div className="w-full h-full bg-white/5 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-brand-cyan transition-all duration-1000 shadow-[0_0_10px_rgba(6,182,212,0.5)]"
                            style={{ width: isPast ? '100%' : isActive ? '50%' : '0%' }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Intelligence Side Panel */}
        <div className="space-y-6 md:space-y-8">
          {/* Primary Action Card */}
          {isComplete && (
            <div className="glass-panel p-6 rounded-[32px] border-emerald-500/20 bg-gradient-to-br from-emerald-500/[0.03] to-transparent">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-7 h-7" />
                </div>
                <div>
                  <h3 className="text-lg font-black text-white tracking-tight">Export Complete</h3>
                  <p className="text-[10px] font-bold text-emerald-500/80 uppercase tracking-widest">High Fidelity Rendered</p>
                </div>
              </div>

              <div className="space-y-3">
                <Link href={`/jobs/${job.id}/download`} className="block">
                  <Button variant="glow" size="lg" className="w-full font-black text-xs uppercase tracking-[0.2em]">
                    <Download className="w-4 h-4 mr-2" />
                    Download Master
                  </Button>
                </Link>
                <Button variant="secondary" size="lg" onClick={openEdit} className="w-full font-black text-xs uppercase tracking-[0.2em]">
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Remix & Iteratue
                </Button>
              </div>

              <div className="mt-8 pt-6 border-t border-white/5 space-y-2">
                <div className="text-[10px] font-black uppercase tracking-widest text-gray-600 mb-3">Project Deliverables</div>
                {videoUrl && (
                  <a href={videoUrl} target="_blank" rel="noreferrer" className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors group">
                    <div className="flex items-center gap-3">
                      <Film className="w-4 h-4 text-gray-500 group-hover:text-brand-cyan transition-colors" />
                      <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Video Output</span>
                    </div>
                    <ExternalLink className="w-3 h-3 text-gray-600" />
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Stats & Tools */}
          <div className="space-y-6">
            <div className="glass-panel p-6 rounded-[32px] border-white/5">
              <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 mb-6 flex items-center gap-2">
                <Activity className="w-4 h-4 text-brand-cyan" />
                Media Intelligence
              </h3>
              <MediaStats intelligence={job.media_intelligence ?? undefined} />
            </div>

            {job.qc_result && (
              <div className="glass-panel p-6 rounded-[32px] border-white/5">
                <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 mb-6 flex items-center gap-2">
                  <Shield className="w-4 h-4 text-brand-violet" />
                  Quality Control
                </h3>
                <QCScoreBoard qcResult={job.qc_result} />
              </div>
            )}

            {job.brand_safety_result && <BrandSafetyCard result={job.brand_safety_result} />}
            {job.ab_test_result && <ABTestVariants result={job.ab_test_result} />}

            {/* Phase 7: Pro Studio Intelligence */}
            {isComplete && (
              <div className="glass-panel p-6 rounded-[32px] border-brand-cyan/20 bg-brand-cyan/[0.02]">
                <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 mb-6 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-brand-cyan" />
                  Pro Studio Mastering
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 rounded-2xl bg-white/5 border border-white/5">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                        <Activity className="w-4 h-4" />
                      </div>
                      <span className="text-[10px] font-bold text-gray-300 uppercase tracking-widest">Audio Mastering</span>
                    </div>
                    <span className="text-[10px] font-black text-emerald-400 uppercase tracking-tighter">STUDIO GRADE</span>
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-2xl bg-white/5 border border-white/5">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                        <Film className="w-4 h-4" />
                      </div>
                      <span className="text-[10px] font-bold text-gray-300 uppercase tracking-widest">Scene Match</span>
                    </div>
                    <span className="text-[10px] font-black text-blue-400 uppercase tracking-tighter">AI CONSISTENT</span>
                  </div>

                  {job.scout_result?.assets?.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-white/5">
                      <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-3">Scouted Stock Manifest</p>
                      <div className="grid grid-cols-2 gap-2">
                        {job.scout_result.assets.slice(0, 4).map((asset: any, i: number) => (
                          <div key={i} className="aspect-video bg-white/5 rounded-lg overflow-hidden border border-white/5 relative group">
                            {asset.preview_url ? (
                              <img src={asset.preview_url} alt="Stock" className="w-full h-full object-cover opacity-60 group-hover:opacity-100 transition-opacity" />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center">
                                <Film className="w-4 h-4 text-gray-700" />
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Manual Edit Overlay */}
      {showEdit && (
        <div className="fixed inset-0 z-[100] bg-obsidian-950/80 backdrop-blur-xl flex items-center justify-center p-4">
          <div className="w-full max-w-2xl glass-heavy border-white/10 rounded-[40px] p-8 md:p-10 relative overflow-hidden animate-in fade-in zoom-in-95 duration-300">
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-10">
              <div>
                <h3 className="text-2xl font-black text-white tracking-tight mb-2">Configure Studio</h3>
                <p className="text-sm text-gray-500">Fine-tune your creative parameters for the next iteration.</p>
              </div>
              <button onClick={() => setShowEdit(false)} className="p-3 bg-white/5 hover:bg-white/10 rounded-2xl transition-all">
                <RotateCcw className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                { key: 'tier', label: 'Processing Tier', options: ['pro', 'standard'] },
                { key: 'platform', label: 'Target Platform', options: ['youtube', 'tiktok', 'instagram', 'linkedin'] },
                { key: 'theme', label: 'Style Theme', options: ['cinematic', 'energetic', 'minimal', 'modern', 'professional'] },
                { key: 'mood', label: 'Mood/Tone', options: ['professional', 'cinematic', 'energetic', 'minimal'] },
                { key: 'ratio', label: 'Aspect Ratio', options: ['16:9', '9:16', '1:1'] },
                { key: 'pacing', label: 'Edit Pacing', options: ['fast', 'medium', 'slow'] },
                { key: 'transition_style', label: 'Transition Style', options: ['cut', 'dissolve', 'wipe'] },
                { key: 'speed_profile', label: 'Speed Profile', options: ['slow', 'balanced', 'fast'] },
                { key: 'subtitle_preset', label: 'Subtitle Preset', options: ['platform_default', 'broadcast', 'social'] },
                { key: 'color_profile', label: 'Color Profile', options: ['natural', 'cinematic', 'punchy'] },
              ].map((field) => (
                <div key={field.key} className="space-y-2">
                  <label className="text-[10px] font-black uppercase tracking-widest text-gray-500 ml-1">{field.label}</label>
                  <select
                    value={(editForm as any)[field.key]}
                    onChange={(e) => setEditForm(s => ({ ...s, [field.key]: e.target.value }))}
                    className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-brand-cyan/50 transition-colors uppercase font-bold tracking-wider"
                  >
                    {field.options.map(opt => <option key={opt} value={opt} className="bg-obsidian-900">{opt}</option>)}
                  </select>
                </div>
              ))}
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-gray-500 ml-1">Transition Seconds</label>
                <input
                  type="number"
                  min={0.1}
                  max={1.5}
                  step={0.05}
                  value={editForm.transition_duration}
                  onChange={(e) => setEditForm(s => ({ ...s, transition_duration: Number(e.target.value) || 0.25 }))}
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-brand-cyan/50 transition-colors font-bold tracking-wider"
                />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-gray-500 ml-1">Skin Protect Strength</label>
                <input
                  type="number"
                  min={0}
                  max={1}
                  step={0.1}
                  value={editForm.skin_protect_strength}
                  onChange={(e) => setEditForm(s => ({ ...s, skin_protect_strength: Number(e.target.value) || 0.5 }))}
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-brand-cyan/50 transition-colors font-bold tracking-wider"
                />
              </div>
            </div>

            {editError && <div className="mt-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs font-bold">{editError}</div>}

            <div className="flex items-center justify-end gap-4 mt-12">
              <Button variant="secondary" size="lg" onClick={() => setShowEdit(false)} className="px-8 font-black text-xs uppercase tracking-widest">Cancel</Button>
              <Button variant="glow" size="lg" onClick={submitEdit} loading={editSubmitting} className="px-10 font-black text-xs uppercase tracking-widest">Execute Edit</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944 11.955 11.955 0 012.382 7.984C2.382 7.984 1 18 12 18c11 0 10-10.016 10-10.016z" />
    </svg>
  );
}
