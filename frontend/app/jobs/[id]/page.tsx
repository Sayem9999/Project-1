'use client';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';

type Job = { id: number; status: string; progress_message: string };

export default function JobStatusPage() {
  const params = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);

  useEffect(() => {
    // Initial fetch
    fetchJob();
    const timer = setInterval(fetchJob, 2500);
    return () => clearInterval(timer);

    async function fetchJob() {
      const res = await apiFetch(`/jobs/${params.id}`);
      if (!res.ok) return;
      setJob(await res.json());
    }
  }, [params.id]);

  // Calculate progress percentage based on message
  const getProgress = (status: string, message: string) => {
    if (status === 'complete') return 100;
    if (status === 'failed') return 100;
    if (message?.includes('Analyzing')) return 25;
    if (message?.includes('AI Director')) return 50;
    if (message?.includes('Rendering')) return 75;
    if (message?.includes('Starting')) return 10;
    return 5;
  };

  const progress = job ? getProgress(job.status, job.progress_message) : 0;
  const isComplete = job?.status === 'complete';
  const isFailed = job?.status === 'failed';

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <div className="glass-panel relative overflow-hidden rounded-2xl p-8 sm:p-12">
        {/* Ambient Background */}
        <div className="absolute -top-24 -right-24 h-64 w-64 rounded-full bg-brand-cyan/10 blur-3xl"></div>
        <div className="absolute top-1/2 -left-24 h-64 w-64 rounded-full bg-brand-magenta/10 blur-3xl"></div>

        <div className="relative space-y-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl text-glow">
            {isComplete ? 'Production Complete' : isFailed ? 'Production Failed' : 'Production in Progress'}
          </h1>

          <p className="text-lg text-slate-400">
            {job?.progress_message || 'Initializing studio...'}
          </p>

          {/* Progress Bar */}
          <div className="relative h-4 w-full overflow-hidden rounded-full bg-slate-800/50">
            <div
              className={`absolute top-0 left-0 h-full transition-all duration-1000 ease-out ${isFailed ? 'bg-red-500' : 'bg-gradient-to-r from-brand-cyan to-brand-violet'
                }`}
              style={{ width: `${progress}%` }}
            >
              {/* Shimmer effect */}
              {!isComplete && !isFailed && (
                <div className="absolute inset-0 animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/25 to-transparent"></div>
              )}
            </div>
          </div>

          {/* Status Details */}
          <div className="flex justify-between text-xs font-mono text-slate-500 uppercase tracking-widest">
            <span>Job ID: {params.id}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>

          {/* Actions */}
          <div className="pt-4">
            {isComplete && (
              <Link
                href={`/jobs/${params.id}/download`}
                className="inline-flex items-center justify-center rounded-lg bg-emerald-500 px-8 py-4 font-bold text-slate-950 shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-transform hover:scale-105 active:scale-95"
              >
                <svg className="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                Download Video
              </Link>
            )}

            {isFailed && (
              <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-red-400">
                An error occurred during production. Please try again.
              </div>
            )}

            {!isComplete && !isFailed && (
              <div className="text-slate-500">
                <span className="inline-block animate-pulse">●</span> AI Director is working...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
