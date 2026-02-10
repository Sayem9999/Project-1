'use client';
import { useCallback, useEffect, useMemo, useRef, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import MediaStats from '@/components/dashboard/MediaStats';
import QCScoreBoard from '@/components/dashboard/QCScoreBoard';
import { ArrowLeft, Download, RotateCcw, Share2, MoreHorizontal, Film, Activity, CheckCircle2, AlertCircle } from 'lucide-react';

import BrandSafetyCard from '@/components/dashboard/BrandSafetyCard';
import ABTestVariants from '@/components/dashboard/ABTestVariants';
import { apiRequest, ApiError, clearAuth, API_ORIGIN, getWebSocketUrl } from '@/lib/api';

interface Job {
  id: number;
  status: string;
  progress_message: string;
  theme?: string;
  pacing?: string;
  mood?: string;
  ratio?: string;
  platform?: string;
  brand_safety?: string;
  output_path?: string;
  thumbnail_path?: string;
  created_at: string;
  updated_at?: string;
  tier?: string;
  credits_cost?: number;
  media_intelligence?: any;
  qc_result?: any;
  director_plan?: any;
  brand_safety_result?: any;
  ab_test_result?: any;
}

export default function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
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
  });

  const fetchJob = useCallback(async () => {
    try {
      const data = await apiRequest<Job>(`/jobs/${resolvedParams.id}`, { auth: true });
      setJob(data);
    } catch (err: any) {
      if (err instanceof ApiError && err.isAuth) {
        clearAuth();
        router.push('/login');
        return;
      }
      setError(err instanceof ApiError ? err.message : 'Job not found');
    }
  }, [resolvedParams.id, router]);

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
    });
    setEditError('');
    setShowEdit(true);
  };

  const submitEdit = async () => {
    if (!job) return;
    setEditSubmitting(true);
    setEditError('');
    try {
      const idempotencyKey =
        typeof crypto !== 'undefined' ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
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
    const interval = setInterval(fetchJob, 15000);
    return () => clearInterval(interval);
  }, [fetchJob, router]);

  useEffect(() => {
    if (!resolvedParams.id) return;
    const ws = new WebSocket(getWebSocketUrl(`/ws/jobs/${resolvedParams.id}`));
    socketRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        setJob((prev) =>
          prev
            ? {
                ...prev,
                status: payload.status ?? prev.status,
                progress_message: payload.message ?? prev.progress_message,
              }
            : prev
        );
        if (payload.status === 'complete' || payload.status === 'failed') {
          ws.close();
          fetchJob();
        }
      } catch {
        // ignore
      }
    };

    ws.onerror = () => {
      ws.close();
    };

    return () => {
      ws.close();
    };
  }, [fetchJob, resolvedParams.id]);

  const stages = [
    { key: 'intel', label: 'Intelligence', icon: <Activity className="w-4 h-4" /> },
    { key: 'director', label: 'Strategy', icon: <Film className="w-4 h-4" /> },
    { key: 'platform', label: 'Adaptation', icon: <Share2 className="w-4 h-4" /> },
    { key: 'render', label: 'Rendering', icon: <Download className="w-4 h-4" /> },
    { key: 'qc', label: 'QC & Eval', icon: <CheckCircle2 className="w-4 h-4" /> },
  ];

  const getCurrentStage = (message: string) => {
    if (!message) return 0;
    if (message.includes('Intel')) return 0;
    if (message.includes('Director')) return 1;
    if (message.includes('Platform') || message.includes('Adapt') || message.includes('Specialist')) return 2;
    if (message.includes('Render') || message.includes('Compiling')) return 3;
    if (message.includes('Review') || message.includes('Quality') || message.includes('QC')) return 4;
    if (message.includes('complete') || message.includes('Ready')) return 5;
    return 0;
  };

  const currentStage = job ? getCurrentStage(job.progress_message) : 0;

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center">
        <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center text-red-500 mb-4">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold mb-2">Error Loading Project</h2>
        <p className="text-gray-400 mb-6">{error}</p>
        <Link href="/dashboard">
          <button className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white font-medium transition-colors">
            Back to Dashboard
          </button>
        </Link>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <div className="w-16 h-16 relative mb-6">
          <div className="absolute inset-0 border-4 border-white/10 rounded-full" />
          <div className="absolute inset-0 border-4 border-t-brand-cyan rounded-full animate-spin" />
        </div>
        <p className="text-gray-400 animate-pulse">Loading Studio...</p>
      </div>
    );
  }

  const isComplete = job.status === 'complete';
  const isFailed = job.status === 'failed';
  const isProcessing = job.status === 'processing' || job.status === 'queued';
  const videoUrl = job.output_path
    ? (job.output_path.startsWith('http') ? job.output_path : `${API_ORIGIN}/${job.output_path}`)
    : null;
  const thumbnailUrl = job.thumbnail_path
    ? (job.thumbnail_path.startsWith('http') ? job.thumbnail_path : `${API_ORIGIN}/${job.thumbnail_path}`)
    : null;
  const lastUpdated = job.updated_at ? new Date(job.updated_at) : new Date(job.created_at);

  const timelineSteps = useMemo(() => {
    return stages.map((stage, index) => {
      const isComplete = index < currentStage;
      const isActive = index === currentStage;
      return {
        ...stage,
        status: isComplete ? 'complete' : isActive ? 'active' : 'pending',
      };
    });
  }, [stages, currentStage]);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-12">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm font-medium">Back to Projects</span>
        </Link>
        <div className="flex items-center gap-3">
          {isProcessing && (
            <button
              onClick={handleCancel}
              className="px-3 py-1.5 text-xs rounded-lg bg-red-500/10 text-red-300 hover:bg-red-500/20 transition-colors"
            >
              Cancel Job
            </button>
          )}
          {isFailed && (
            <button
              onClick={handleRetry}
              className="px-3 py-1.5 text-xs rounded-lg bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20 transition-colors"
            >
              Retry Job
            </button>
          )}
          <button
            onClick={openEdit}
            className="px-3 py-1.5 text-xs rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
          >
            Edit Settings
          </button>
          <span className="px-3 py-1 bg-white/5 rounded-lg text-xs font-mono text-gray-500">ID: {job.id}</span>
          <button className="p-2 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white">
            <MoreHorizontal className="w-5 h-5" />
          </button>
        </div>
      </div>

      {actionError && (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {actionError}
        </div>
      )}

      {/* Cinematic Player Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Video Player Container */}
          <div className="aspect-video bg-black rounded-3xl overflow-hidden relative group border border-white/10 shadow-2xl shadow-black/50">
            {videoUrl && isComplete ? (
              <video src={videoUrl} controls className="w-full h-full object-contain" />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center relative bg-obsidian-900">
                {/* Ambient Glow */}
                <div className="absolute inset-0 bg-gradient-radial from-brand-cyan/5 to-transparent opacity-50 animate-pulse-slow" />

                {/* Processing Visual */}
                <div className="relative z-10 text-center">
                  <div className="w-20 h-20 mx-auto mb-6 relative">
                    <div className="absolute inset-0 border-4 border-brand-cyan/20 rounded-full" />
                    <div className="absolute inset-0 border-4 border-t-brand-cyan rounded-full animate-spin" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-xs font-mono font-bold text-brand-cyan">{Math.round((currentStage / stages.length) * 100)}%</span>
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2 blink">{job.progress_message || 'Initializing...'}</h3>
                  <p className="text-sm text-brand-cyan font-mono">Running Agents: {stages[Math.min(currentStage, stages.length - 1)].label}</p>
                </div>
              </div>
            )}
          </div>

          {/* Pipeline Visualizer */}
          <div className="glass-panel p-6 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between relative z-10">
              {stages.map((stage, i) => {
                const isActive = i === currentStage;
                const isPast = i < currentStage;
                return (
                  <div key={stage.key} className="flex flex-col items-center gap-3 relative z-10 flex-1">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ${isActive ? 'bg-brand-cyan text-black scale-110 shadow-glow' :
                      isPast ? 'bg-emerald-500 text-black' :
                        'bg-white/5 text-gray-600'
                      }`}>
                      {isPast ? <CheckCircle2 className="w-5 h-5" /> : stage.icon}
                    </div>
                    <span className={`text-xs font-medium transition-colors ${isActive ? 'text-white' : 'text-gray-500'}`}>{stage.label}</span>

                    {/* Connecting Line */}
                    {i < stages.length - 1 && (
                      <div className="absolute top-5 left-1/2 w-full h-[2px] -z-10">
                        <div className="w-full h-full bg-white/5" />
                        <div
                          className="absolute inset-0 bg-brand-cyan transition-all duration-700"
                          style={{ width: isPast ? '100%' : isActive ? '50%' : '0%' }}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Timeline */}
          <div className="glass-panel p-6 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-gray-400">Timeline</h3>
              <span className="text-xs text-gray-500">Last update: {lastUpdated.toLocaleString()}</span>
            </div>
            <div className="space-y-4">
              {timelineSteps.map((step) => (
                <div key={step.key} className="flex items-start gap-4">
                  <div
                    className={`mt-1 w-3 h-3 rounded-full border ${
                      step.status === 'complete'
                        ? 'bg-emerald-400 border-emerald-400'
                        : step.status === 'active'
                        ? 'bg-brand-cyan border-brand-cyan animate-pulse'
                        : 'bg-white/10 border-white/10'
                    }`}
                  />
                  <div>
                    <div className="text-sm text-white font-semibold">{step.label}</div>
                    <div className="text-xs text-gray-500">
                      {step.status === 'active' ? job.progress_message || 'In progress' : step.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Side: Data Bento */}
        <div className="space-y-6">
          {/* Download / Action Card */}
          {isComplete && (
            <div className="glass-panel p-6 rounded-2xl flex flex-col gap-4">
              <div className="flex items-center gap-4 mb-2">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-white">Export Ready</h3>
                  <p className="text-xs text-gray-400">Successfully rendered in 1080p</p>
                </div>
              </div>
              <Link
                href={`/jobs/${job.id}/download`}
                className="w-full py-3 bg-white text-black font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-gray-100 transition-colors"
              >
                <Download className="w-4 h-4" />
                Download Video
              </Link>
              <div className="space-y-2">
                {videoUrl && (
                  <a
                    href={videoUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="w-full py-2 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-gray-300 flex items-center justify-between"
                  >
                    <span>Open Output File</span>
                    <span className="text-brand-cyan">MP4</span>
                  </a>
                )}
                {thumbnailUrl && (
                  <a
                    href={thumbnailUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="w-full py-2 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-gray-300 flex items-center justify-between"
                  >
                    <span>Open Thumbnail</span>
                    <span className="text-brand-violet">JPG</span>
                  </a>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <button className="py-3 bg-white/5 hover:bg-white/10 rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2">
                  <Share2 className="w-4 h-4" /> Share
                </button>
                <Link href="/dashboard/upload" className="py-3 bg-white/5 hover:bg-white/10 rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2">
                  <RotateCcw className="w-4 h-4" /> New
                </Link>
              </div>
            </div>
          )}

          {/* Intelligence Stats */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-gray-400 mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4 text-brand-cyan" />
              MEDIA INTELLIGENCE
            </h3>
            <MediaStats intelligence={job.media_intelligence} />
          </div>

          {/* QC Score */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-sm font-bold text-gray-400 mb-4 flex items-center gap-2">
              <Shield className="w-4 h-4 text-brand-violet" />
              QUALITY CONTROL
            </h3>
            {/* Using a simplified version or the component if it fits */}
            <div className="scale-95 origin-top-left -mb-4">
              <QCScoreBoard qcResult={job.qc_result} />
            </div>
          </div>

          {/* Brand Safety */}
          {job.brand_safety_result && (
            <div className="glass-panel rounded-2xl overflow-hidden border border-white/5 transition-all duration-300 hover:border-emerald-500/20">
              <BrandSafetyCard result={job.brand_safety_result} />
            </div>
          )}

          {/* A/B Variants */}
          {job.ab_test_result && (
            <div className="glass-panel rounded-2xl overflow-hidden border border-white/5 transition-all duration-300 hover:border-brand-violet/20">
              <ABTestVariants result={job.ab_test_result} />
            </div>
          )}
        </div>
      </div>

      {showEdit && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-6">
          <div className="w-full max-w-2xl bg-slate-900 border border-white/10 rounded-3xl p-6 space-y-6">
            <div>
              <h3 className="text-xl font-bold text-white">Manual Edit</h3>
              <p className="text-sm text-gray-400">Create a new version using updated settings.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <select
                value={editForm.tier}
                onChange={(e) => setEditForm((s) => ({ ...s, tier: e.target.value }))}
                className="bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
              >
                <option value="pro">Pro</option>
                <option value="standard">Standard</option>
              </select>
              <select
                value={editForm.platform}
                onChange={(e) => setEditForm((s) => ({ ...s, platform: e.target.value }))}
                className="bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
              >
                <option value="youtube">YouTube</option>
                <option value="tiktok">TikTok</option>
                <option value="instagram">Instagram</option>
                <option value="linkedin">LinkedIn</option>
              </select>
              <select
                value={editForm.theme}
                onChange={(e) => setEditForm((s) => ({ ...s, theme: e.target.value }))}
                className="bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
              >
                <option value="cinematic">Cinematic</option>
                <option value="energetic">High Energy</option>
                <option value="minimal">Minimalist</option>
                <option value="documentary">Docu-Style</option>
                <option value="professional">Professional</option>
              </select>
              <select
                value={editForm.pacing}
                onChange={(e) => setEditForm((s) => ({ ...s, pacing: e.target.value }))}
                className="bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
              >
                <option value="fast">Fast</option>
                <option value="medium">Medium</option>
                <option value="slow">Slow</option>
              </select>
              <select
                value={editForm.mood}
                onChange={(e) => setEditForm((s) => ({ ...s, mood: e.target.value }))}
                className="bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
              >
                <option value="professional">Professional</option>
                <option value="cinematic">Cinematic</option>
                <option value="energetic">Energetic</option>
                <option value="minimal">Minimal</option>
              </select>
              <select
                value={editForm.ratio}
                onChange={(e) => setEditForm((s) => ({ ...s, ratio: e.target.value }))}
                className="bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
              >
                <option value="16:9">16:9</option>
                <option value="9:16">9:16</option>
                <option value="1:1">1:1</option>
              </select>
              <select
                value={editForm.brand_safety}
                onChange={(e) => setEditForm((s) => ({ ...s, brand_safety: e.target.value }))}
                className="bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-sm text-white"
              >
                <option value="standard">Standard</option>
                <option value="strict">Strict</option>
                <option value="relaxed">Relaxed</option>
              </select>
            </div>
            {editError && (
              <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm text-red-200">
                {editError}
              </div>
            )}
            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowEdit(false)}
                className="px-4 py-2 rounded-lg bg-white/5 text-gray-300 hover:bg-white/10"
              >
                Close
              </button>
              <button
                onClick={submitEdit}
                disabled={editSubmitting}
                className="px-4 py-2 rounded-lg bg-brand-cyan text-black font-semibold hover:bg-brand-accent disabled:opacity-60"
              >
                {editSubmitting ? 'Creating...' : 'Create Edit'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Shield({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944 11.955 11.955 0 012.382 7.984C2.382 7.984 1 18 12 18c11 0 10-10.016 10-10.016z" />
    </svg>
  )
}
