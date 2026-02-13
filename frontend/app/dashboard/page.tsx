'use client';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Plus, Clock, Play, Film, HardDrive, LayoutGrid, Search, ArrowRight, Sparkles } from 'lucide-react';
import Image from 'next/image';
import { apiRequest, ApiError, clearAuth, API_ORIGIN, getWebSocketUrl } from '@/lib/api';
import MediaLibrary from '@/components/dashboard/MediaLibrary';
import { Button } from '@/components/ui/Button';

interface Job {
    id: number;
    status: string;
    progress_message: string;
    output_path: string;
    thumbnail_path: string;
    created_at: string;
}

export default function DashboardPage() {
    const router = useRouter();
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [userName, setUserName] = useState<string | null>(null);
    const [userId, setUserId] = useState<number | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [activeView, setActiveView] = useState<'projects' | 'media'>('projects');
    const [mounted, setMounted] = useState(false);

    // Guard against hydration mismatches and ensure client-only data loading
    useEffect(() => {
        setMounted(true);
    }, []);

    const activeCount = useMemo(() => {
        if (!Array.isArray(jobs)) return 0;
        return jobs.filter((job) => job?.status === 'processing').length;
    }, [jobs]);

    useEffect(() => {
        if (!mounted) return;

        const token = localStorage.getItem('token');
        if (!token) {
            router.push('/login');
            return;
        }

        const load = async () => {
            try {
                const [me, data] = await Promise.all([
                    apiRequest<{ id: number; full_name?: string; email?: string }>('/auth/me', { auth: true }),
                    apiRequest<Job[]>('/jobs', { auth: true })
                ]);

                // Safe state updates
                setUserName(me?.full_name || me?.email || 'Creator');
                setUserId(me?.id || null);
                setJobs(Array.isArray(data) ? data : []);
                setLoading(false);
            } catch (err: any) {
                console.error('[Dashboard] Load failed', err);
                if (err instanceof ApiError && err.isAuth) {
                    clearAuth();
                    router.push('/login');
                    return;
                }
                setError(err instanceof ApiError ? err.message : 'Server unreachable or offline');
                setLoading(false);
            }
        };

        load();
    }, [router, mounted]);

    useEffect(() => {
        if (!userId || !mounted) return;

        const url = getWebSocketUrl(`/ws/user/${userId}`);
        let ws: WebSocket | null = null;

        try {
            ws = new WebSocket(url);
            ws.onmessage = (event) => {
                try {
                    const payload = JSON.parse(event.data);
                    setJobs((prev) => {
                        if (!Array.isArray(prev)) return [];
                        return prev.map((j) =>
                            j.id === payload.job_id
                                ? {
                                    ...j,
                                    status: payload.status ?? j.status,
                                    progress_message: payload.message ?? j.progress_message,
                                }
                                : j
                        );
                    });
                } catch (e) {
                    console.error('[Dashboard] WebSocket parse error', e);
                }
            };
        } catch (err) {
            console.error('[Dashboard] WebSocket connection failed', err);
        }

        return () => ws?.close();
    }, [userId, mounted]);

    if (!mounted) return null;

    const getStatusParams = (status: string) => {
        switch (status) {
            case 'complete':
                return { color: 'text-emerald-400', bg: 'bg-emerald-400/10', label: 'Ready', dot: 'bg-emerald-400' };
            case 'failed':
                return { color: 'text-red-400', bg: 'bg-red-400/10', label: 'Failed', dot: 'bg-red-400' };
            case 'processing':
                return { color: 'text-brand-cyan', bg: 'bg-brand-cyan/10', label: 'Processing', dot: 'bg-brand-cyan animate-pulse' };
            default:
                return { color: 'text-gray-400', bg: 'bg-gray-400/10', label: 'Queued', dot: 'bg-gray-400' };
        }
    };

    return (
        <div className="max-w-[1600px] mx-auto space-y-6 md:space-y-8">
            {/* Hero Stats Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 glass-panel rounded-3xl p-6 md:p-8 relative overflow-hidden group border-white/5">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-brand-cyan/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-brand-cyan/20 transition-colors duration-700" />

                    <div className="relative z-10">
                        <div className="flex items-center gap-2 mb-2">
                            <Sparkles className="w-4 h-4 text-brand-cyan" />
                            <span className="text-xs font-black uppercase tracking-[0.2em] text-gray-500">Studio Workspace</span>
                        </div>
                        <h2 className="text-2xl md:text-3xl font-black tracking-tight mb-2">Welcome back, {userName || 'Creator'}</h2>
                        <p className="text-gray-400 mb-8 max-w-lg text-sm md:text-base leading-relaxed">
                            Your studio is ready. You have <span className="text-white font-bold">{activeCount}</span> active projects and <span className="text-white font-bold">{jobs.length}</span> total exports.
                        </p>

                        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
                            <Link href="/dashboard/upload">
                                <Button variant="glow" size="lg" className="w-full sm:w-auto">
                                    <Plus className="w-5 h-5 mr-2" />
                                    <span>New Project</span>
                                </Button>
                            </Link>
                            <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                                View Tutorials
                            </Button>
                        </div>
                    </div>
                </div>

                <div className="glass-panel rounded-3xl p-6 md:p-8 flex flex-col justify-between relative overflow-hidden border-white/5 bg-gradient-to-br from-white/[0.03] to-transparent">
                    <div className="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-brand-violet/10 to-transparent" />
                    <div>
                        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 mb-1">Total Impact</div>
                        <h3 className="text-gray-400 font-medium mb-1">Total Exports</h3>
                        <p className="text-4xl md:text-5xl font-black tracking-tighter text-white">{jobs.length}</p>
                    </div>
                    <div className="relative z-10 mt-6 md:mt-0">
                        <div className="flex items-center gap-2 text-xs font-bold text-brand-violet uppercase tracking-widest">
                            <Film className="w-4 h-4" />
                            <span>Efficiency Boosted</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Content Section */}
            <div>
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 border-b border-white/5 gap-4">
                    <div className="flex items-center gap-6 md:gap-8">
                        <button
                            onClick={() => setActiveView('projects')}
                            className={`flex items-center gap-2 pb-4 -mb-px border-b-2 transition-all ${activeView === 'projects' ? 'border-brand-cyan text-white font-black uppercase tracking-widest text-xs' : 'border-transparent text-gray-500 hover:text-gray-300 font-bold text-xs uppercase tracking-widest'}`}
                        >
                            <LayoutGrid className="w-4 h-4" />
                            <span>Recent Projects</span>
                        </button>
                        <button
                            onClick={() => setActiveView('media')}
                            className={`flex items-center gap-2 pb-4 -mb-px border-b-2 transition-all ${activeView === 'media' ? 'border-brand-cyan text-white font-black uppercase tracking-widest text-xs' : 'border-transparent text-gray-500 hover:text-gray-300 font-bold text-xs uppercase tracking-widest'}`}
                        >
                            <HardDrive className="w-4 h-4" />
                            <span>Media Library</span>
                        </button>
                    </div>

                    {activeView === 'projects' && (
                        <div className="flex items-center gap-2 pb-4 md:pb-0">
                            {['All', 'Processing', 'Completed'].map(filter => (
                                <button key={filter} className="px-3 py-1.5 text-[10px] sm:text-xs font-bold uppercase tracking-widest rounded-lg hover:bg-white/5 text-gray-500 hover:text-white transition-all">
                                    {filter}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {activeView === 'media' ? (
                    <MediaLibrary />
                ) : loading ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="aspect-video rounded-3xl bg-white/5 animate-pulse" />
                        ))}
                    </div>
                ) : error ? (
                    <div className="glass-panel border border-red-500/20 rounded-3xl p-10 text-center">
                        <div className="text-xs font-black uppercase tracking-widest text-red-500 mb-2">Sync Error</div>
                        <p className="text-gray-400 mb-6 text-sm">{error}</p>
                        <Button variant="secondary" onClick={() => window.location.reload()}>Retry Connection</Button>
                    </div>
                ) : jobs.length === 0 ? (
                    <div className="glass-panel border-dashed border-2 border-white/5 rounded-3xl p-12 text-center flex flex-col items-center">
                        <div className="w-20 h-20 mb-6 rounded-3xl bg-gradient-to-br from-brand-cyan/20 to-brand-violet/20 flex items-center justify-center">
                            <Film className="w-10 h-10 text-brand-cyan" />
                        </div>
                        <h3 className="text-xl font-bold mb-2">Start your first masterpiece</h3>
                        <p className="text-gray-400 mb-8 text-sm max-w-xs">Upload clips and let our AI agents orchestrate your creative vision.</p>
                        <Link href="/dashboard/upload">
                            <Button variant="glow" size="lg" className="px-10">
                                Create Project
                            </Button>
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {/* New Project Ghost Card */}
                        <Link href="/dashboard/upload" className="aspect-video rounded-3xl border-2 border-dashed border-white/5 hover:border-brand-cyan/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all group flex flex-col items-center justify-center gap-3">
                            <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center group-hover:bg-brand-cyan/20 group-hover:scale-110 transition-all duration-500">
                                <Plus className="w-6 h-6 text-gray-500 group-hover:text-brand-cyan" />
                            </div>
                            <span className="font-black text-gray-500 group-hover:text-white uppercase tracking-[0.2em] text-[10px]">New Project</span>
                        </Link>

                        {Array.isArray(jobs) && jobs.map((job) => {
                            if (!job) return null;
                            const status = getStatusParams(job.status);

                            // Safely build media URL, ensuring we don't fetch if no path exists
                            const mediaPath = job.thumbnail_path || job.output_path;
                            const mediaUrl = mediaPath
                                ? (mediaPath.startsWith('http') ? mediaPath : `${API_ORIGIN}/${mediaPath}`)
                                : null;

                            const isVideo = mediaUrl?.toLowerCase().endsWith('.mp4');

                            return (
                                <Link
                                    key={job.id}
                                    href={`/jobs/${job.id}`}
                                    className="group relative aspect-video rounded-3xl overflow-hidden bg-white/5 border border-white/5 hover:border-brand-cyan/50 transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-brand-cyan/10"
                                >
                                    {/* Thumbnail Media */}
                                    <div className="absolute inset-0">
                                        {mediaUrl ? (
                                            isVideo ? (
                                                <video
                                                    src={mediaUrl}
                                                    className="w-full h-full object-cover opacity-50 group-hover:opacity-80 group-hover:scale-110 transition-all duration-1000"
                                                    muted
                                                    playsInline
                                                />
                                            ) : (
                                                <Image
                                                    src={mediaUrl}
                                                    alt={`Project ${job.id}`}
                                                    fill
                                                    sizes="(max-width: 1024px) 100vw, 25vw"
                                                    className="object-cover opacity-50 group-hover:opacity-80 group-hover:scale-110 transition-all duration-1000"
                                                    unoptimized
                                                />
                                            )
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center bg-white/5">
                                                <Film className="w-12 h-12 text-white/5 group-hover:text-white/10 transition-colors" />
                                            </div>
                                        )}
                                        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent opacity-90" />
                                    </div>

                                    {/* Status Badge */}
                                    <div className="absolute top-4 left-4">
                                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl glass-heavy ${status.bg} border-white/5 shadow-2xl`}>
                                            <div className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
                                            <span className={`text-[10px] font-black uppercase tracking-widest ${status.color}`}>{status.label}</span>
                                        </div>
                                    </div>

                                    {/* Content */}
                                    <div className="absolute bottom-0 left-0 right-0 p-6 transform translate-y-1 group-hover:translate-y-0 transition-transform">
                                        <h3 className="text-lg font-black text-white mb-2 leading-tight group-hover:text-brand-cyan transition-colors truncate tracking-tight">Project #{job.id}</h3>
                                        <div className="flex items-center justify-between text-[10px] text-gray-500 font-extrabold uppercase tracking-[0.15em]">
                                            <span className="flex items-center gap-2">
                                                <Clock className="w-3 h-3" />
                                                {job.created_at ? new Date(job.created_at).toLocaleDateString() : 'Recent'}
                                            </span>
                                            {job.status === 'processing' && (
                                                <div className="flex flex-col gap-1 w-full mt-2">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-brand-cyan animate-pulse">
                                                            {job.progress_message?.split(']')[1]?.trim() || job.progress_message || 'Processing...'}
                                                        </span>
                                                        <span className="text-[9px] text-gray-600 font-black">
                                                            {job.progress_message?.includes('[AI]') ? 'HOLLYWOOD PIPELINE' : 'AGENTIC WORKFLOW'}
                                                        </span>
                                                    </div>
                                                    <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-gradient-to-r from-brand-cyan to-brand-violet transition-all duration-1000 ease-out"
                                                            style={{
                                                                width: job.progress_message?.includes('10%') ? '10%' :
                                                                    job.progress_message?.includes('20%') ? '20%' :
                                                                        job.progress_message?.includes('50%') ? '50%' :
                                                                            job.progress_message?.includes('80%') ? '80%' : '15%'
                                                            }}
                                                        />
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Hover Overlay Play Icon */}
                                    {job.status === 'complete' && (
                                        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                                            <div className="w-14 h-14 rounded-full bg-brand-cyan/90 flex items-center justify-center shadow-2xl shadow-brand-cyan/40 scale-90 group-hover:scale-100 transition-transform duration-500">
                                                <Play className="w-6 h-6 text-black ml-1" fill="currentColor" />
                                            </div>
                                        </div>
                                    )}
                                </Link>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
