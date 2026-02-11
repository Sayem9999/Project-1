'use client';
import { memo } from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
    icon: LucideIcon;
    title: string;
    value: string | number;
    subtext: string;
    color: 'cyan' | 'emerald' | 'violet' | 'amber' | 'rose';
    progress?: number;
}

export default memo(function StatCard({ icon: Icon, title, value, subtext, color, progress }: StatCardProps) {
    const colors = {
        cyan: 'from-cyan-500/20 to-cyan-500/5 text-cyan-400 border-cyan-500/20 bg-cyan-400',
        emerald: 'from-emerald-500/20 to-emerald-500/5 text-emerald-400 border-emerald-500/20 bg-emerald-400',
        violet: 'from-violet-500/20 to-violet-500/5 text-violet-400 border-violet-500/20 bg-violet-400',
        amber: 'from-amber-500/20 to-amber-500/5 text-amber-400 border-amber-500/20 bg-amber-400',
        rose: 'from-rose-500/20 to-rose-500/5 text-rose-400 border-rose-500/20 bg-rose-400',
    };

    const config = colors[color] || colors.cyan;
    const [gradient, , , progressBg] = config.split(' ');

    return (
        <div className={`glass-panel border rounded-3xl p-6 bg-gradient-to-br ${gradient} transition-all hover:scale-[1.02] hover:shadow-2xl`}>
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-2xl bg-white/5 ${config.split(' ')[2]}`}>
                    <Icon className="w-6 h-6" />
                </div>
                {progress !== undefined && (
                    <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest bg-white/5 px-2 py-1 rounded-lg">
                        {progress}% Limit
                    </div>
                )}
            </div>
            <div className="space-y-1">
                <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
                <p className="text-3xl font-display font-bold text-white tracking-tight">{value}</p>
                <div className="flex items-center gap-2 group">
                    <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">{subtext}</span>
                </div>
            </div>

            {progress !== undefined && (
                <div className="mt-4 h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                    <div className={`h-full ${progressBg}`} style={{ width: `${progress}%` }} />
                </div>
            )}
        </div>
    );
});
