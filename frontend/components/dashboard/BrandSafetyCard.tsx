import React from 'react';
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';

interface Violation {
    type: string;
    severity: string;
    timestamp?: number;
    description: string;
}

interface BrandSafetyResult {
    is_safe: boolean;
    violations: Violation[];
    risk_score: number;
    recommendations: string[];
}

interface BrandSafetyCardProps {
    result?: BrandSafetyResult;
}

export default function BrandSafetyCard({ result }: BrandSafetyCardProps) {
    if (!result) return null;

    return (
        <div className="bg-[#1a1a24] rounded-xl p-5 border border-white/5 space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-400 flex items-center gap-2">
                    <Shield className="w-4 h-4 text-emerald-400" />
                    BRAND SAFETY
                </h3>
                <div className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${result.is_safe ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                    {result.is_safe ? 'SAFE' : 'REJECTED'}
                </div>
            </div>

            <div className="flex items-center gap-4">
                <div className="relative w-16 h-16">
                    <svg className="w-full h-full -rotate-90">
                        <circle cx="32" cy="32" r="28" className="fill-none stroke-white/5" strokeWidth="4" />
                        <circle
                            cx="32"
                            cy="32"
                            r="28"
                            className={`fill-none ${result.risk_score > 50 ? 'stroke-red-500' : result.risk_score > 20 ? 'stroke-yellow-500' : 'stroke-emerald-500'}`}
                            strokeWidth="4"
                            strokeLinecap="round"
                            strokeDasharray={`${(result.risk_score / 100) * 176} 176`}
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-sm font-bold text-white">{result.risk_score}</span>
                        <span className="text-[8px] text-gray-500 uppercase">Risk</span>
                    </div>
                </div>

                <div className="flex-1">
                    <p className="text-xs text-gray-400 leading-relaxed">
                        {result.violations.length > 0
                            ? `Detected ${result.violations.length} potential risk factors.`
                            : 'No policy violations detected in transcript or visuals.'}
                    </p>
                </div>
            </div>

            {result.violations.length > 0 && (
                <div className="space-y-2">
                    {result.violations.map((v, i) => (
                        <div key={i} className="flex gap-3 p-2 bg-white/5 rounded-lg border border-white/5">
                            <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${v.severity === 'high' ? 'text-red-500' : 'text-yellow-500'}`} />
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-0.5">
                                    <span className="text-[10px] font-bold text-white uppercase">{v.type}</span>
                                    <span className="text-[10px] text-gray-500">{v.severity} risk</span>
                                </div>
                                <p className="text-[11px] text-gray-400 truncate">{v.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {result.recommendations.length > 0 && (
                <div className="pt-2 border-t border-white/5">
                    <p className="text-[10px] font-bold text-gray-500 uppercase mb-2">Recommendations</p>
                    <ul className="space-y-1">
                        {result.recommendations.map((rec, i) => (
                            <li key={i} className="flex items-start gap-2 text-[11px] text-gray-300">
                                <div className="w-1 h-1 rounded-full bg-brand-cyan mt-1.5 flex-shrink-0" />
                                {rec}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
