'use client';
import { memo } from 'react';
import { Trophy, Mail, Hash } from 'lucide-react';

interface LeaderboardEntry {
    email: string;
    count: number;
}

interface UsageLeaderboardProps {
    entries: LeaderboardEntry[];
}

export default memo(function UsageLeaderboard({ entries }: UsageLeaderboardProps) {
    return (
        <div className="glass-panel p-8 rounded-[32px] border-white/5 relative overflow-hidden bg-gradient-to-br from-white/[0.02] to-transparent">
            <div className="flex items-center justify-between mb-8 relative z-10">
                <div>
                    <h3 className="text-lg font-black tracking-tight text-white mb-1">Impact Leaderboard</h3>
                    <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Top Creators by Production Volume</p>
                </div>
                <Trophy className="w-6 h-6 text-amber-400" />
            </div>

            <div className="space-y-4 relative z-10">
                {entries.length > 0 ? (
                    entries.map((entry, index) => (
                        <div
                            key={entry.email}
                            className="flex items-center justify-between p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all group"
                        >
                            <div className="flex items-center gap-4">
                                <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-black text-xs ${index === 0 ? 'bg-amber-400/20 text-amber-400' :
                                        index === 1 ? 'bg-slate-300/20 text-slate-300' :
                                            index === 2 ? 'bg-orange-400/20 text-orange-400' :
                                                'bg-white/5 text-gray-500'
                                    }`}>
                                    {index + 1}
                                </div>
                                <div>
                                    <div className="text-sm font-black text-white group-hover:text-brand-cyan transition-colors truncate max-w-[150px]">
                                        {entry.email.split('@')[0]}
                                    </div>
                                    <div className="text-[10px] font-bold text-gray-600 uppercase tracking-widest truncate max-w-[150px]">
                                        {entry.email}
                                    </div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-sm font-black text-white">{entry.count}</div>
                                <div className="text-[10px] font-bold text-gray-600 uppercase tracking-widest">JOBS</div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="text-center py-8">
                        <p className="text-xs font-bold text-gray-600 uppercase tracking-widest">Initial telemetry pending...</p>
                    </div>
                )}
            </div>
        </div>
    );
});
