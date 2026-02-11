'use client';
import { memo } from 'react';

interface TrendData {
    date: string;
    count: number;
}

interface SystemTrendsProps {
    trends: {
        jobs_by_day: TrendData[];
        failures_by_day: TrendData[];
        users_by_day: TrendData[];
    };
}

export default memo(function SystemTrends({ trends }: SystemTrendsProps) {
    const trendConfigs = [
        { label: 'Jobs', data: trends.jobs_by_day, color: 'bg-cyan-500' },
        { label: 'Failures', data: trends.failures_by_day, color: 'bg-red-500' },
        { label: 'New Users', data: trends.users_by_day, color: 'bg-emerald-500' },
    ];

    return (
        <div className="lg:col-span-3 bg-slate-900/30 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
            <h3 className="text-lg font-semibold text-white mb-4">7-Day Trends</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {trendConfigs.map((trend) => {
                    const max = Math.max(...trend.data.map((d) => d.count), 1);
                    return (
                        <div key={trend.label} className="rounded-2xl bg-white/5 border border-white/10 p-4">
                            <div className="text-xs text-gray-400 mb-3">{trend.label}</div>
                            <div className="space-y-2">
                                {trend.data.map((point) => (
                                    <div key={point.date} className="flex items-center gap-3">
                                        <span className="text-[10px] text-gray-500 w-16">{point.date}</span>
                                        <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full ${trend.color}`}
                                                style={{ width: `${Math.round((point.count / max) * 100)}%` }}
                                            />
                                        </div>
                                        <span className="text-xs text-gray-300 w-6 text-right">{point.count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
});
