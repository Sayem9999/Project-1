'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Users, Video, HardDrive, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

interface SystemStats {
    users: {
        total: number;
    };
    jobs: {
        total: number;
        recent_24h: number;
    };
    storage: {
        bytes: number;
        files: number;
        percent: number;
        limit_gb: number;
        used_gb: number;
    };
}

export default function AdminDashboardPage() {
    const router = useRouter();
    const [stats, setStats] = useState<SystemStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            router.push('/login');
            return;
        }

        fetch(`${API_BASE}/admin/stats`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then(res => {
                if (res.status === 403) throw new Error('Access Denied');
                if (!res.ok) throw new Error('Failed to fetch stats');
                return res.json();
            })
            .then(data => {
                setStats(data);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    }, [router]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
                <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-4">
                    <Activity className="w-8 h-8 text-red-400" />
                </div>
                <h2 className="text-xl font-bold text-white mb-2">Error Loading Dashboard</h2>
                <p className="text-gray-400">{error}</p>
            </div>
        );
    }

    if (!stats) return null;

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">System Overview</h1>
                <p className="text-gray-400">Monitor system performance and resource usage</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Users Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 bg-[#12121a] border border-white/10 rounded-2xl relative overflow-hidden group hover:border-cyan-500/30 transition-colors"
                >
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Users className="w-24 h-24 text-cyan-500" />
                    </div>
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-cyan-500/10 rounded-xl">
                            <Users className="w-6 h-6 text-cyan-400" />
                        </div>
                        <h3 className="text-lg font-medium text-gray-200">Total Users</h3>
                    </div>
                    <div className="text-4xl font-bold text-white mb-1">{stats.users.total}</div>
                    <p className="text-sm text-gray-500">Registered accounts</p>
                </motion.div>

                {/* Jobs Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="p-6 bg-[#12121a] border border-white/10 rounded-2xl relative overflow-hidden group hover:border-violet-500/30 transition-colors"
                >
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Video className="w-24 h-24 text-violet-500" />
                    </div>
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-violet-500/10 rounded-xl">
                            <Video className="w-6 h-6 text-violet-400" />
                        </div>
                        <h3 className="text-lg font-medium text-gray-200">Total Jobs</h3>
                    </div>
                    <div className="text-4xl font-bold text-white mb-1">{stats.jobs.total}</div>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span className="text-emerald-400 font-medium">+{stats.jobs.recent_24h}</span>
                        <span>in last 24h</span>
                    </div>
                </motion.div>

                {/* Storage Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="p-6 bg-[#12121a] border border-white/10 rounded-2xl relative overflow-hidden group hover:border-emerald-500/30 transition-colors"
                >
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                        <HardDrive className="w-24 h-24 text-emerald-500" />
                    </div>
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-emerald-500/10 rounded-xl">
                            <HardDrive className="w-6 h-6 text-emerald-400" />
                        </div>
                        <h3 className="text-lg font-medium text-gray-200">Storage Usage</h3>
                    </div>
                    <div className="mb-4">
                        <div className="flex items-end gap-2 mb-1">
                            <span className="text-4xl font-bold text-white">{stats.storage.used_gb}</span>
                            <span className="text-lg text-gray-400 mb-1">/ {stats.storage.limit_gb} GB</span>
                        </div>
                        <p className="text-sm text-gray-500">{stats.storage.files} files tracked</p>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-white/5 rounded-full h-2 overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-1000 ${stats.storage.percent > 80 ? 'bg-red-500' :
                                    stats.storage.percent > 50 ? 'bg-yellow-500' : 'bg-emerald-500'
                                }`}
                            style={{ width: `${Math.min(stats.storage.percent, 100)}%` }}
                        />
                    </div>
                    <p className="text-xs text-right text-gray-500 mt-2">{stats.storage.percent}% used</p>
                </motion.div>
            </div>
        </div>
    );
}
