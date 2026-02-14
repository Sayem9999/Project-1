'use client';

import { Activity, Gauge, RefreshCw, ShieldAlert, Zap } from 'lucide-react';
import { Button } from '@/components/ui/Button';

type AutonomyStatus = {
    enabled: boolean;
    running: boolean;
    profile_mode: string;
    profile: Record<string, number>;
    available_profiles: string[];
    metrics: {
        run_count: number;
        heal_count: number;
        improve_count: number;
        skip_high_load_count: number;
    };
    last_heal_at?: string | null;
    last_improve_at?: string | null;
    last_result?: {
        idle?: boolean;
        high_load?: boolean;
        load?: {
            cpu_percent?: number;
            memory_percent?: number;
        };
    };
};

type Props = {
    autonomy: AutonomyStatus | null;
    loading: boolean;
    actionLoading: boolean;
    onRefresh: () => void;
    onSetMode: (mode: string) => void;
    onRun: (opts: { force_heal?: boolean; force_improve?: boolean }) => void;
};

export default function AutonomyPanel({
    autonomy,
    loading,
    actionLoading,
    onRefresh,
    onSetMode,
    onRun,
}: Props) {
    return (
        <div className="glass-panel p-8 rounded-[32px] border-white/5 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-brand-cyan/5 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2" />
            <div className="relative z-10">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-8">
                    <div>
                        <h3 className="text-lg font-black text-white uppercase tracking-widest mb-1">Autonomy Control Plane</h3>
                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Self-Heal + Self-Improve Runtime</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <Button variant="secondary" onClick={onRefresh} className="text-[10px] font-black uppercase tracking-widest">
                            <RefreshCw className="w-4 h-4 mr-2" /> Refresh
                        </Button>
                    </div>
                </div>

                {loading || !autonomy ? (
                    <div className="text-[10px] font-black uppercase tracking-widest text-gray-500">Loading autonomy status...</div>
                ) : (
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5">
                                <div className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-2">Engine</div>
                                <div className={`text-sm font-black uppercase tracking-widest ${autonomy.running ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {autonomy.running ? 'Running' : 'Stopped'}
                                </div>
                            </div>
                            <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5">
                                <div className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-2">Mode</div>
                                <div className="text-sm font-black uppercase tracking-widest text-brand-cyan">{autonomy.profile_mode}</div>
                            </div>
                            <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5">
                                <div className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-2">Runs</div>
                                <div className="text-sm font-black text-white">{autonomy.metrics.run_count}</div>
                            </div>
                            <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5">
                                <div className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-2">High-Load Skips</div>
                                <div className="text-sm font-black text-amber-400">{autonomy.metrics.skip_high_load_count}</div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                                <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-gray-500">
                                    <Gauge className="w-4 h-4 text-brand-cyan" /> Runtime Load
                                </div>
                                <div className="text-xs font-bold text-gray-300">
                                    CPU: {Number(autonomy.last_result?.load?.cpu_percent || 0).toFixed(1)}%
                                </div>
                                <div className="text-xs font-bold text-gray-300">
                                    Memory: {Number(autonomy.last_result?.load?.memory_percent || 0).toFixed(1)}%
                                </div>
                                <div className={`text-[10px] font-black uppercase tracking-widest ${autonomy.last_result?.high_load ? 'text-amber-400' : 'text-emerald-400'}`}>
                                    {autonomy.last_result?.high_load ? 'High Load Guard Active' : 'Load Within Profile Limits'}
                                </div>
                            </div>
                            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                                <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-gray-500">
                                    <Activity className="w-4 h-4 text-brand-violet" /> Cycle Metrics
                                </div>
                                <div className="text-xs font-bold text-gray-300">Heals: {autonomy.metrics.heal_count}</div>
                                <div className="text-xs font-bold text-gray-300">Improves: {autonomy.metrics.improve_count}</div>
                                <div className="text-xs font-bold text-gray-300">Idle: {autonomy.last_result?.idle ? 'yes' : 'no'}</div>
                            </div>
                        </div>

                        <div className="flex flex-col xl:flex-row xl:items-center gap-4">
                            <div className="flex items-center gap-3">
                                <span className="text-[10px] font-black uppercase tracking-widest text-gray-500">Profile</span>
                                <select
                                    value={autonomy.profile_mode}
                                    onChange={(e) => onSetMode(e.target.value)}
                                    className="bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-[10px] font-black uppercase tracking-widest text-white"
                                    disabled={actionLoading}
                                >
                                    {autonomy.available_profiles.map((mode) => (
                                        <option key={mode} value={mode} className="bg-obsidian-900">
                                            {mode}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex flex-wrap items-center gap-3">
                                <Button variant="secondary" onClick={() => onRun({ force_heal: true })} loading={actionLoading} className="text-[10px] font-black uppercase tracking-widest">
                                    <ShieldAlert className="w-4 h-4 mr-2" /> Force Heal
                                </Button>
                                <Button variant="secondary" onClick={() => onRun({ force_improve: true })} loading={actionLoading} className="text-[10px] font-black uppercase tracking-widest">
                                    <Zap className="w-4 h-4 mr-2" /> Force Improve
                                </Button>
                                <Button variant="glow" onClick={() => onRun({ force_heal: true, force_improve: true })} loading={actionLoading} className="text-[10px] font-black uppercase tracking-widest">
                                    Full Cycle
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
