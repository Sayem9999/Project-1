import React from 'react';

interface Metric {
    name: string;
    score: number;
    max: number;
    weight: number;
    reasoning: string;
}

interface QCScoreBoardProps {
    qcResult?: {
        approved: boolean;
        feedback?: string;
        metrics?: {
            technical_integrity: number;
            aesthetic_appeal: number;
            pacing_flow: number;
            platform_optimization: number;
            audience_retention: number;
        };
        overall_score?: number;
    };
}

export default function QCScoreBoard({ qcResult }: QCScoreBoardProps) {
    if (!qcResult) return null;

    const scores = [
        { label: 'Technical', val: qcResult.metrics?.technical_integrity ?? 0, color: 'bg-blue-500' },
        { label: 'Aesthetic', val: qcResult.metrics?.aesthetic_appeal ?? 0, color: 'bg-purple-500' },
        { label: 'Pacing', val: qcResult.metrics?.pacing_flow ?? 0, color: 'bg-pink-500' },
        { label: 'Platform', val: qcResult.metrics?.platform_optimization ?? 0, color: 'bg-orange-500' },
        { label: 'Retention', val: qcResult.metrics?.audience_retention ?? 0, color: 'bg-green-500' },
    ];

    return (
        <div className="bg-[#1a1a24] rounded-xl p-6 border border-white/5">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span className="text-emerald-400">🛡️</span> Quality Assessment
                </h3>
                <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${qcResult.approved
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-red-500/20 text-red-400 border border-red-500/30'
                    }`}>
                    {qcResult.approved ? 'APPROVED' : 'NEEDS REVISION'}
                </div>
            </div>

            <div className="flex gap-4 mb-6">
                {/* Overall Score Circle */}
                <div className="relative w-24 h-24 flex-shrink-0">
                    <svg className="w-full h-full -rotate-90">
                        <circle cx="48" cy="48" r="40" className="fill-none stroke-white/10" strokeWidth="6" />
                        <circle
                            cx="48" cy="48" r="40"
                            className={`fill-none ${qcResult.approved ? 'stroke-emerald-500' : 'stroke-orange-500'}`}
                            strokeWidth="6"
                            strokeLinecap="round"
                            strokeDasharray={`${(qcResult.overall_score ?? 0) / 10 * 251} 251`}
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-2xl font-bold text-white">{qcResult.overall_score?.toFixed(1) ?? 0}</span>
                        <span className="text-[10px] text-gray-500 uppercase">Score</span>
                    </div>
                </div>

                <div className="flex-1 space-y-3">
                    {scores.map((s) => (
                        <div key={s.label}>
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-400">{s.label}</span>
                                <span className="text-white font-mono">{s.val}/10</span>
                            </div>
                            <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${s.color} rounded-full transition-all duration-1000`}
                                    style={{ width: `${(s.val / 10) * 100}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {qcResult.feedback && (
                <div className="mt-4 p-4 bg-white/5 rounded-lg border border-white/5">
                    <p className="text-xs text-gray-500 uppercase mb-1 font-bold">Producer Feedback</p>
                    <p className="text-sm text-gray-300 italic">"{qcResult.feedback}"</p>
                </div>
            )}
        </div>
    );
}
