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
    const timer = setInterval(async () => {
      const res = await apiFetch(`/jobs/${params.id}`);
      if (!res.ok) return;
      setJob(await res.json());
    }, 2500);
    return () => clearInterval(timer);
  }, [params.id]);

  return <section className="space-y-4"><h1 className="text-3xl font-semibold">Processing job #{params.id}</h1><p>Status: <span className="font-semibold">{job?.status ?? 'loading...'}</span></p><p>{job?.progress_message}</p>{job?.status === 'complete' && <Link className="rounded bg-cyan-400 px-4 py-2 font-semibold text-slate-950" href={`/jobs/${params.id}/download`}>Go to download</Link>}</section>;
}
