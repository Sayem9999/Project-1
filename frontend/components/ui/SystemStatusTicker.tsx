'use client';
import { useEffect, useState } from 'react';
import { apiRequest } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldCheck, Zap } from 'lucide-react';

export default function SystemStatusTicker() {
    const [stats, setStats] = useState<{ nodes: number; endpoints: number; services: number } | null>(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await apiRequest('/maintenance/graph'); // Note: This might require auth depending on how public we want it
                if (data && data.stats) {
                    setStats(data.stats);
                }
            } catch (e) {
                // Fallback or silent fail for landing page
            }
        };
        fetchStats();
    }, []);

    return (
        <div className="w-full bg-black/40 backdrop-blur-md border-y border-white/5 py-2">
            <div className="container mx-auto px-6 flex items-center justify-between text-[10px] font-bold tracking-[0.2em] uppercase text-gray-500">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-gray-400">Network Operational</span>
                    </div>

                    <AnimatePresence mode="wait">
                        {stats && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="hidden md:flex items-center gap-6"
                            >
                                <div className="flex items-center gap-2">
                                    <Activity className="w-3 h-3 text-brand-cyan" />
                                    <span>{stats.nodes} Neural Nodes</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <ShieldCheck className="w-3 h-3 text-brand-violet" />
                                    <span>{stats.services} Specialized Services</span>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <div className="flex items-center gap-2 text-brand-cyan">
                    <Zap className="w-3 h-3 fill-brand-cyan" />
                    <span>V4 Autonmous Engine Live</span>
                </div>
            </div>
        </div>
    );
}
