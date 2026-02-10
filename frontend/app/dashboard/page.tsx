'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Plus, Clock, MoreVertical, Play, Film } from 'lucide-react';
import Image from 'next/image';
import { apiRequest, ApiError, clearAuth, API_ORIGIN } from '@/lib/api';

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
    const [error, setError] = useState<string | null>(null);
    const activeCount = jobs.filter((job) => job.status === 'processing').length;

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            router.push('/login');
            return;
        }

        const load = async () => {
            try {
                const [me, data] = await Promise.all([
                    apiRequest<{ full_name?: string; email?: string }>('/auth/me', { auth: true }),
                    apiRequest<Job[]>('/jobs', { auth: true })
                ]);
                setUserName(me.full_name || me.email || 'Creator');
                setJobs(data);
                setLoading(false);
            } catch (err) {
                if (err instanceof ApiError && err.isAuth) {
                    clearAuth();
                    router.push('/login');
                    return;
                }
                setError(err instanceof ApiError ? err.message : 'Failed to load dashboard');
                setLoading(false);
            }
        };

        load();
    }, [router]);

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
        <div className="max-w-[1600px] mx-auto space-y-8">
            {/* Hero Stats Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2 glass-panel rounded-3xl p-8 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-brand-cyan/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-brand-cyan/20 transition-colors duration-700" />

                    <div className="relative z-10">
                        <h2 className="text-3xl font-display font-bold mb-2">Welcome back, {userName || 'Creator'}</h2>
                        <p className="text-gray-400 mb-8 max-w-lg">
                            Your studio is ready. You have <span className="text-white font-semibold">{activeCount}</span> active projects and <span className="text-white font-semibold">{jobs.length}</span> total exports.
                        </p>

                        <div className="flex items-center gap-4">
                            <Link href="/dashboard/upload">
                                <button className="px-6 py-3 bg-white text-black rounded-xl font-semibold hover:bg-gray-200 transition-colors flex items-center gap-2 shadow-lg shadow-white/10">
                                    <Plus className="w-5 h-5" />
                                    <span>New Project</span>
                                </button>
                            </Link>
                            <button className="px-6 py-3 glass-card rounded-xl font-semibold text-white hover:bg-white/5 transition-colors">
                                View Tutorials
                            </button>
                        </div>
                    </div>
                </div>

                <div className="glass-panel rounded-3xl p-8 flex flex-col justify-between relative overflow-hidden">
                    <div className="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-brand-violet/20 to-transparent" />
                    <div>
                        <h3 className="text-gray-400 font-medium mb-1">Total Exports</h3>
                        <p className="text-4xl font-display font-bold">{jobs.length}</p>
                    </div>
                    <div className="relative z-10 mt-4">
                        <div className="flex items-center gap-2 text-sm text-brand-violet">
                            <Film className="w-4 h-4" />
                            <span>12 hrs saved this month</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Config / Projects Section */}
            <div>
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold">Recent Projects</h2>
                    <div className="flex items-center gap-2">
                        <button className="px-3 py-1.5 text-sm rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">All</button>
                        <button className="px-3 py-1.5 text-sm rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">Processing</button>
                        <button className="px-3 py-1.5 text-sm rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">Completed</button>
                    </div>
                </div>

                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="aspect-[16/9] rounded-2xl bg-white/5 animate-pulse" />
                        ))}
                    </div>
                ) : error ? (
                    <div className="glass-panel border border-red-500/20 rounded-3xl p-10 text-center">
                        <div className="text-sm text-red-400 mb-2">Dashboard Error</div>
                        <p className="text-gray-400 mb-6">{error}</p>
                        <button
                            onClick={() => router.refresh()}
                            className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white font-medium transition-colors"
                        >
                            Retry
                        </button>
                    </div>
                ) : jobs.length === 0 ? (
                    <div className="glass-panel border-dashed border-2 border-white/10 rounded-3xl p-12 text-center">
                        <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-brand-cyan/20 to-brand-violet/20 flex items-center justify-center text-4xl">
                            Studio
                        </div>
                        <h3 className="text-xl font-bold mb-2">Start your first masterpiece</h3>
                        <p className="text-gray-400 mb-8">Upload clips and let our AI agents handle the rest.</p>
                        <Link href="/dashboard/upload">
                            <button className="px-8 py-3 bg-brand-cyan text-black font-bold rounded-xl hover:bg-brand-accent transition-colors">
                                Create Project
                            </button>
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {/* New Project Ghost Card */}
                        <Link href="/dashboard/upload" className="aspect-[16/9] rounded-2xl border-2 border-dashed border-white/10 hover:border-brand-cyan/50 bg-white/5 hover:bg-white/10 transition-all group flex flex-col items-center justify-center gap-3">
                            <div className="w-14 h-14 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-brand-cyan/20 transition-colors">
                                <Plus className="w-6 h-6 text-gray-400 group-hover:text-brand-cyan" />
                            </div>
                            <span className="font-semibold text-gray-400 group-hover:text-white">New Project</span>
                        </Link>

                        {jobs.map((job) => {
                            const status = getStatusParams(job.status);
                            return (
                                <Link
                                    key={job.id}
                                    href={`/jobs/${job.id}`}
                                    className="group relative aspect-[16/9] rounded-2xl overflow-hidden bg-obsidian-900 border border-white/10 hover:border-brand-cyan/50 transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-brand-cyan/10"
                                >
                                    {/* Thumbnail Image */}
                                    <div className="absolute inset-0 relative">
                                        {job.thumbnail_path || job.output_path ? (
                                            <Image
                                                src={job.thumbnail_path
                                                    ? (job.thumbnail_path.startsWith('http') ? job.thumbnail_path : `${API_ORIGIN}/${job.thumbnail_path}`)
                                                    : (job.output_path?.startsWith('http') ? job.output_path : `${API_ORIGIN}/${job.output_path}`)}
                                                alt={`Project ${job.id}`}
                                                fill
                                                sizes="(max-width: 1024px) 100vw, 25vw"
                                                className="object-cover opacity-60 group-hover:opacity-100 group-hover:scale-105 transition-all duration-500"
                                                unoptimized
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center bg-white/5">
                                                <Film className="w-12 h-12 text-white/20" />
                                            </div>
                                        )}
                                        <div className="absolute inset-0 bg-gradient-to-t from-obsidian-950 via-obsidian-950/20 to-transparent opacity-80" />
                                    </div>

                                    {/* Status Badge */}
                                    <div className="absolute top-3 left-3">
                                        <div className={`flex items-center gap-2 px-2.5 py-1 rounded-lg backdrop-blur-md ${status.bg} border border-white/5`}>
                                            <div className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
                                            <span className={`text-xs font-medium ${status.color}`}>{status.label}</span>
                                        </div>
                                    </div>

                                    {/* Actions (Hover) */}
                                    <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-2 group-hover:translate-x-0 duration-300">
                                        <button className="p-2 rounded-lg bg-black/60 hover:bg-white text-white hover:text-black backdrop-blur-md transition-colors">
                                            <MoreVertical className="w-4 h-4" />
                                        </button>
                                    </div>

                                    {/* Content */}
                                    <div className="absolute bottom-0 left-0 right-0 p-5">
                                        <h3 className="text-lg font-bold text-white mb-1 leading-tight group-hover:text-brand-cyan transition-colors">Project #{job.id}</h3>
                                        <div className="flex items-center justify-between text-xs text-gray-400">
                                            <span className="flex items-center gap-1">
                                                <Clock className="w-3 h-3" />
                                                {new Date(job.created_at).toLocaleDateString()}
                                            </span>
                                            {job.status === 'processing' && <span className="text-brand-cyan animate-pulse">Encoding...</span>}
                                        </div>
                                    </div>

                                    {/* Hover Overlay Play Icon */}
                                    {job.status === 'complete' && (
                                        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                                            <div className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/20">
                                                <Play className="w-5 h-5 text-white ml-0.5" fill="currentColor" />
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
