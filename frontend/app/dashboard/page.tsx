'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

interface Job {
    id: number;
    status: string;
    progress_message: string;
    output_path?: string;
    thumbnail_path?: string;
    created_at: string;
}

export default function DashboardPage() {
    const router = useRouter();
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            router.push('/login');
            return;
        }

        fetch(`${API_BASE}/jobs`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then(res => {
                if (!res.ok) throw new Error('Failed to fetch');
                return res.json();
            })
            .then(data => {
                setJobs(data);
                setLoading(false);
            })
            .catch(() => {
                setLoading(false);
            });
    }, [router]);

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'complete':
                return <span className="px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Complete</span>;
            case 'failed':
                return <span className="px-2.5 py-1 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">Failed</span>;
            case 'processing':
                return <span className="px-2.5 py-1 rounded-lg text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 animate-pulse">Processing</span>;
            default:
                return <span className="px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-500/10 text-gray-400 border border-gray-500/20">Queued</span>;
        }
    };

    return (
        <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">My Projects</h1>
                    <p className="text-gray-400">Manage and create your AI video projects</p>
                </div>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="aspect-video bg-white/5 rounded-2xl animate-pulse" />
                    ))}
                </div>
            ) : jobs.length === 0 ? (
                <div className="text-center py-24 bg-white/5 border border-white/5 rounded-3xl">
                    <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center text-4xl">
                        🎬
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-3">No projects yet</h2>
                    <p className="text-gray-400 mb-8 max-w-sm mx-auto">Upload your first video to start creating cinematic content with AI.</p>
                    <Link
                        href="/dashboard/upload"
                        className="inline-flex items-center gap-2 px-8 py-4 bg-white text-black rounded-xl font-bold hover:bg-gray-100 transition-all hover:scale-[1.02] active:scale-[0.98]"
                    >
                        Create New Project
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {/* Create New Card */}
                    <Link href="/dashboard/upload" className="group relative aspect-[4/3] rounded-2xl border-2 border-dashed border-white/10 hover:border-cyan-500/50 bg-white/5 hover:bg-white/10 transition-all flex flex-col items-center justify-center gap-4">
                        <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-cyan-500/20 transition-colors">
                            <span className="text-2xl text-gray-400 group-hover:text-cyan-400">+</span>
                        </div>
                        <span className="font-semibold text-gray-400 group-hover:text-white">New Project</span>
                    </Link>

                    {/* Project Cards */}
                    {jobs.map(job => (
                        <Link
                            key={job.id}
                            href={`/jobs/${job.id}`}
                            className="group relative aspect-[4/3] bg-[#12121a] rounded-2xl border border-white/10 hover:border-white/20 overflow-hidden transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-cyan-500/10"
                        >
                            {/* Thumbnail */}
                            <div className="absolute inset-x-0 top-0 h-2/3 bg-gradient-to-br from-gray-800 to-black group-hover:scale-105 transition-transform duration-500">
                                {job.output_path && (job.output_path.match(/\.(jpg|jpeg|png|webp)$/i) || job.thumbnail_path) ? (
                                    <img
                                        src={job.thumbnail_path
                                            ? (job.thumbnail_path.startsWith('http') ? job.thumbnail_path : `${API_BASE.replace('/api', '')}/${job.thumbnail_path}`)
                                            : (job.output_path?.startsWith('http') ? job.output_path : `${API_BASE.replace('/api', '')}/${job.output_path}`)}
                                        alt={`Project ${job.id}`}
                                        className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-4xl opacity-50">
                                        🎬
                                    </div>
                                )}
                                <div className="absolute inset-0 bg-gradient-to-t from-[#12121a] to-transparent" />
                            </div>

                            {/* Status Line */}
                            <div className="absolute top-4 right-4">
                                {getStatusBadge(job.status)}
                            </div>

                            {/* Content */}
                            <div className="absolute inset-x-0 bottom-0 p-5">
                                <h3 className="text-lg font-bold text-white mb-1 group-hover:text-cyan-400 transition-colors">
                                    Project #{job.id}
                                </h3>
                                <div className="flex items-center justify-between text-xs text-gray-500">
                                    <span>{new Date(job.created_at).toLocaleDateString()}</span>
                                    <span>{job.status === 'processing' ? 'Processing...' : '03:24'}</span>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
