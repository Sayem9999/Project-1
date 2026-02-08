'use client';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';

type Job = { id: number; status: string; progress_message: string; theme: string };

import { AgentConsole } from '@/components/ui/AgentConsole';
import { VideoPlayer } from '@/components/ui/VideoPlayer';

// ... (imports)

export default function JobStatusPage() {
  const params = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [downloadUrl, setDownloadUrl] = useState('');

  useEffect(() => {
    fetchJob();
    const timer = setInterval(fetchJob, 2000); // Faster polling for console effect
    return () => clearInterval(timer);

    async function fetchJob() {
      const res = await apiFetch(`/jobs/${params.id}`);
      if (!res.ok) return;
      const data = await res.json();
      setJob(data);
      if (data.status === 'complete' && !downloadUrl) {
        // Construct download URL (using API base or proxy)
        // Assuming API serves it at /jobs/:id/download
        setDownloadUrl(`${process.env.NEXT_PUBLIC_API_BASE}/jobs/${params.id}/download`);
      }
    }
  }, [params.id, downloadUrl]);

  // Calculate progress percentage and ETA based on message
  const getProgressInfo = (status: string, message: string) => {
    if (status === 'complete') return { progress: 100, eta: 'Complete!', stage: 'Done' };
    if (status === 'failed') return { progress: 100, eta: 'Failed', stage: 'Error' };

    // Stage-based progress
    if (message?.includes('Memory') || message?.includes('Starting'))
      return { progress: 10, eta: '~2 min', stage: 'Initializing' };
    if (message?.includes('Director') || message?.includes('Planning'))
      return { progress: 25, eta: '~1.5 min', stage: 'AI Director' };
    if (message?.includes('Specialists') || message?.includes('Cutter'))
      return { progress: 45, eta: '~1 min', stage: 'AI Specialists' };
    if (message?.includes('Rendering'))
      return { progress: 70, eta: '~45 sec', stage: 'Rendering' };
    if (message?.includes('QC') || message?.includes('Review'))
      return { progress: 85, eta: '~20 sec', stage: 'QC Review' };
    if (message?.includes('Subtitle') || message?.includes('Meta'))
      return { progress: 95, eta: '~10 sec', stage: 'Finalizing' };

    return { progress: 5, eta: '~2 min', stage: 'Queued' };
  };

  const progressInfo = job ? getProgressInfo(job.status, job.progress_message) : { progress: 0, eta: '', stage: '' };
  const isComplete = job?.status === 'complete';
  const isFailed = job?.status === 'failed';

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* Left Column: Visuals */}
        <div className="space-y-6">
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl text-glow">
            {isComplete ? 'Production Ready' : isFailed ? 'Production Failed' : 'AI Production Live'}
          </h1>

          {isComplete && downloadUrl ? (
            <div className="animate-in zoom-in duration-500">
              <VideoPlayer src={downloadUrl} />
              <div className="mt-4 flex gap-4">
                <a href={downloadUrl} download className="btn-primary flex-1 text-center py-3">
                  Download Master File
                </a>
                <button className="px-4 py-3 rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-300">
                  Share
                </button>
              </div>
            </div>
          ) : (
            <div className="aspect-video rounded-xl bg-slate-900/50 border border-slate-800 flex items-center justify-center relative overflow-hidden group">
              {/* Shimmer Effect */}
              <div className="absolute inset-0 loading-shimmer"></div>
              <div className="absolute inset-0 bg-gradient-to-br from-brand-cyan/5 to-brand-violet/5"></div>
              <div className="text-center space-y-4 relative z-10">
                <div className="relative mx-auto w-20 h-20 animate-float">
                  <div className="absolute inset-0 rounded-full border-t-2 border-brand-cyan animate-spin"></div>
                  <div className="absolute inset-2 rounded-full border-r-2 border-brand-violet animate-spin" style={{ animationDirection: 'reverse' }}></div>
                  <div className="absolute inset-4 rounded-full border-b-2 border-brand-fuchsia animate-spin"></div>
                </div>
                <div className="space-y-1">
                  <p className="text-slate-300 font-semibold progress-pulse">{job?.progress_message || 'Initializing...'}</p>
                  <p className="text-slate-500 text-xs font-mono">PROEDIT STUDIO ENGINE v2.0</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Console & Details */}
        <div className="space-y-6">
          {/* Agent Terminal */}
          <div className="glass-panel p-1 rounded-xl">
            <AgentConsole status={job?.status || 'loading'} lastMessage={job?.progress_message || ''} />
          </div>

          {/* Job Details Card */}
          <div className="glass-panel p-6 rounded-xl space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-white">Production Details</h3>
              {!isComplete && !isFailed && (
                <span className="agent-badge agent-badge-active">
                  {progressInfo.stage}
                </span>
              )}
            </div>

            {/* Progress Bar */}
            {!isComplete && !isFailed && (
              <div className="space-y-2">
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-brand-cyan to-brand-violet transition-all duration-500 ease-out"
                    style={{ width: `${progressInfo.progress}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">{progressInfo.progress}% complete</span>
                  <span className="text-brand-cyan font-medium">ETA: {progressInfo.eta}</span>
                </div>
              </div>
            )}

            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-slate-500">Project ID</dt>
                <dd className="font-mono text-slate-300">{params.id}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Status</dt>
                <dd className={`font-mono ${isComplete ? 'text-emerald-400' : isFailed ? 'text-red-400' : 'text-brand-cyan'}`}>
                  {job?.status?.toUpperCase() || 'LOADING'}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Theme</dt>
                <dd className="text-slate-300 capitalize">{job?.theme || 'Standard'}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Engine</dt>
                <dd className="text-slate-300">Proedit AI v2.0</dd>
              </div>
            </dl>
          </div>
        </div>

      </div>
    </div>
  );
}
