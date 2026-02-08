'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/ui/Navbar';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

interface Job {
    id: number;
    status: string;
    progress_message: string;
    output_path?: string;
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
                return <span className="px-2 py-1 rounded-full text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Complete</span>;
            case 'failed':
                return <span className="px-2 py-1 rounded-full text-xs bg-red-500/20 text-red-400 border border-red-500/30">Failed</span>;
            case 'processing':
                return <span className="px-2 py-1 rounded-full text-xs bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">Processing</span>;
            default:
                return <span className="px-2 py-1 rounded-full text-xs bg-gray-500/20 text-gray-400 border border-gray-500/30">Queued</span>;
        }
    };

    return (
        <main className="min-h-screen bg-[#0a0a0f]">
            <Navbar />

            <div className="container mx-auto px-6 pt-24 pb-16">
                <div className="max-w-4xl mx-auto">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h1 className="text-2xl font-bold text-white">My Projects</h1>
                            <p className="text-gray-400 text-sm">Your video editing history</p>
                        </div>
                        <Link
                            href="/dashboard/upload"
                            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg text-sm font-semibold text-white hover:opacity-90 transition-opacity"
                        >
                            + New Project
                        </Link>
                    </div>

                    {loading ? (
                        <div className="text-center py-16">
                            <div className="w-12 h-12 mx-auto mb-4 relative">
                                <div className="absolute inset-0 rounded-full border-t-2 border-cyan-500 animate-spin" />
                            </div>
                            <p className="text-gray-400">Loading projects...</p>
                        </div>
                    ) : jobs.length === 0 ? (
                        <div className="text-center py-16 bg-[#12121a] border border-white/10 rounded-2xl">
                            <div className="text-5xl mb-4">🎬</div>
                            <h2 className="text-xl font-semibold text-white mb-2">No projects yet</h2>
                            <p className="text-gray-400 mb-6">Upload your first video to get started</p>
                            <Link
                                href="/dashboard/upload"
                                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-xl text-white font-semibold hover:opacity-90 transition-opacity"
                            >
                                Upload Video
                            </Link>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {jobs.map(job => (
                                <Link
                                    key={job.id}
                                    href={`/jobs/${job.id}`}
                                    className="flex items-center justify-between p-4 bg-[#12121a] border border-white/10 rounded-xl hover:border-cyan-500/50 transition-colors"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center text-xl">
                                            🎬
                                        </div>
                                        <div>
                                            <p className="font-medium text-white">Project #{job.id}</p>
                                            <p className="text-sm text-gray-400">{job.progress_message || 'Processing...'}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        {getStatusBadge(job.status)}
                                        <span className="text-xs text-gray-500">
                                            {new Date(job.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}
