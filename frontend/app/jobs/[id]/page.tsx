'use client';
import { useEffect, useMemo, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/ui/Navbar';
import { API_BASE, wsBaseFromApi } from '@/lib/api';

interface Job {
  id: number;
  status: string;
  progress_message: string;
  output_path?: string;
  created_at: string;
}

const statusStyles: Record<string, { icon: string; label: string; bgGlow: string; badge: string }> = {
  complete: {
    icon: '✓',
    label: 'Complete',
    bgGlow: 'from-emerald-500/20',
    badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  },
  failed: {
    icon: '✕',
    label: 'Failed',
    bgGlow: 'from-red-500/20',
    badge: 'bg-red-500/20 text-red-400 border-red-500/30',
  },
  processing: {
    icon: '⟳',
    label: 'Processing',
    bgGlow: 'from-cyan-500/20',
    badge: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  },
  pending: {
    icon: '○',
    label: 'Queued',
    bgGlow: 'from-gray-500/20',
    badge: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  },
};

export default function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    let pollTimer: ReturnType<typeof setInterval> | null = null;

    const fetchJob = async () => {
      try {
        const res = await fetch(`${API_BASE}/jobs/${resolvedParams.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Job not found');
        const data = await res.json();
        setJob(data);
        setError('');
      } catch (err: any) {
        setError(err.message ?? 'Failed to fetch job');
      }
    };

    fetchJob();

    const wsUrl = `${wsBaseFromApi(API_BASE).replace('/api', '')}/ws/jobs/${resolvedParams.id}`;
    let ws: WebSocket | null = null;

    try {
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setJob((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              status: message.status ?? prev.status,
              progress_message: message.message ?? message.progress_message ?? prev.progress_message,
            };
          });
        } catch {
          // ignore non-json ping messages
        }
      };
      ws.onerror = () => {
        pollTimer = setInterval(fetchJob, 3000);
      };
      ws.onclose = () => {
        if (!pollTimer) pollTimer = setInterval(fetchJob, 3000);
      };
    } catch {
      pollTimer = setInterval(fetchJob, 3000);
    }

    return () => {
      if (pollTimer) clearInterval(pollTimer);
      ws?.close();
    };
  }, [resolvedParams.id, router]);

  const statusConfig = useMemo(() => statusStyles[job?.status ?? 'pending'] ?? statusStyles.pending, [job?.status]);

  const stages = [
    { key: 'analysis', label: 'Keyframe Analysis', icon: '🎯' },
    { key: 'director', label: 'Director Planning', icon: '🎬' },
    { key: 'specialists', label: 'AI Specialists', icon: '✨' },
    { key: 'render', label: 'Rendering', icon: '🔧' },
    { key: 'post', label: 'Post-Production', icon: '🎨' },
  ];

  const getCurrentStage = (message: string) => {
    if (message?.includes('FRAME') || message?.includes('keyframe')) return 0;
    if (message?.includes('Director') || message?.includes('MAX')) return 1;
    if (message?.includes('Specialist') || message?.includes('parallel')) return 2;
    if (message?.includes('Render')) return 3;
    if (message?.includes('THUMB') || message?.includes('complete')) return 4;
    return 0;
  };

  const currentStage = job ? getCurrentStage(job.progress_message) : 0;

  return (
    <main className="min-h-screen bg-[#0a0a0f]">
      <Navbar />

      <div className="container mx-auto px-6 pt-24 pb-16">
        <div className="max-w-2xl mx-auto">
          {error ? (
            <div className="text-center py-16">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
                <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">Job Not Found</h2>
              <p className="text-gray-400 mb-6">{error}</p>
              <Link href="/dashboard/upload" className="text-cyan-400 hover:underline">← Back to Upload</Link>
            </div>
          ) : !job ? (
            <div className="text-center py-16">
              <div className="w-16 h-16 mx-auto mb-4 relative">
                <div className="absolute inset-0 rounded-full border-t-2 border-cyan-500 animate-spin" />
              </div>
              <p className="text-gray-400">Loading job...</p>
            </div>
          ) : (
            <>
              <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#12121a] p-8 mb-8">
                <div className={`absolute inset-0 bg-gradient-to-br ${statusConfig.bgGlow} to-transparent opacity-50`} />
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-6">
                    <span className="text-sm text-gray-400">Job #{job.id}</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${statusConfig.badge}`}>{statusConfig.label}</span>
                  </div>

                  {job.status === 'processing' && (
                    <div className="flex justify-center mb-8">
                      <div className="relative w-32 h-32">
                        <svg className="w-full h-full -rotate-90">
                          <circle cx="64" cy="64" r="56" className="fill-none stroke-white/10" strokeWidth="8" />
                          <circle
                            cx="64"
                            cy="64"
                            r="56"
                            className="fill-none stroke-cyan-500"
                            strokeWidth="8"
                            strokeLinecap="round"
                            strokeDasharray={`${((currentStage + 1) / stages.length) * 352} 352`}
                            style={{ transition: 'stroke-dasharray 0.5s ease' }}
                          />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-3xl font-bold text-white">{Math.round(((currentStage + 1) / stages.length) * 100)}%</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {job.status === 'complete' && (
                    <div className="flex justify-center mb-8">
                      <div className="w-24 h-24 rounded-full bg-emerald-500/20 flex items-center justify-center">
                        <svg className="w-12 h-12 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    </div>
                  )}

                  <p className="text-center text-lg text-white font-medium mb-2">{job.progress_message || 'Preparing...'}</p>
                  {job.status === 'processing' && <p className="text-center text-sm text-gray-400">Stage {currentStage + 1} of {stages.length}</p>}
                </div>
              </div>

              {job.status !== 'complete' && job.status !== 'failed' && (
                <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 mb-8">
                  <h3 className="text-sm font-medium text-gray-400 mb-4">Processing Pipeline</h3>
                  <div className="space-y-3">
                    {stages.map((stage, i) => (
                      <div key={stage.key} className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg ${i < currentStage ? 'bg-emerald-500/20' : i === currentStage ? 'bg-cyan-500/20 animate-pulse' : 'bg-white/5'}`}>
                          {stage.icon}
                        </div>
                        <div className="flex-1">
                          <p className={`text-sm font-medium ${i <= currentStage ? 'text-white' : 'text-gray-500'}`}>{stage.label}</p>
                        </div>
                        {i < currentStage && (
                          <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                        {i === currentStage && <div className="w-5 h-5 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {job.status === 'complete' && job.output_path && (
                <div className="space-y-4">
                  <a href={`${API_BASE}/jobs/${job.id}/download`} className="flex items-center justify-center gap-2 w-full py-4 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-xl text-white font-semibold hover:opacity-90 transition-opacity">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download Video
                  </a>
                  <Link href="/dashboard/upload" className="flex items-center justify-center gap-2 w-full py-4 bg-white/10 rounded-xl text-white font-medium hover:bg-white/20 transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Create Another
                  </Link>
                </div>
              )}

              {job.status === 'failed' && (
                <div className="text-center">
                  <Link href="/dashboard/upload" className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 rounded-xl text-white font-medium hover:bg-white/20 transition-colors">
                    Try Again
                  </Link>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </main>
  );
}
