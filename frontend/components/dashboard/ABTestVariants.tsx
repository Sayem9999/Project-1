import React from 'react';
import { Copy, TrendingUp, Sparkles } from 'lucide-react';
import { ABTestResult } from '@/lib/types';

interface ABTestVariantsProps {
    result?: ABTestResult;
}

export default function ABTestVariants({ result }: ABTestVariantsProps) {
    if (!result || !result.variants) return null;

    return (
        <div className="bg-[#1a1a24] rounded-xl p-5 border border-white/5 space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-400 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-brand-violet" />
                    A/B OPTIMIZATION
                </h3>
                <div className="px-2 py-0.5 bg-brand-violet/20 rounded text-[10px] font-bold text-brand-violet border border-brand-violet/30 uppercase">
                    {result.variants.length} VARIANTS
                </div>
            </div>

            <div className="space-y-3">
                {result.variants.map((variant) => (
                    <div key={variant.id} className="group relative bg-white/5 rounded-xl p-4 border border-white/5 hover:border-brand-violet/50 transition-all duration-300">
                        <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                                <div className="w-6 h-6 rounded bg-brand-violet/20 flex items-center justify-center text-[10px] font-bold text-brand-violet border border-brand-violet/30">
                                    {variant.id}
                                </div>
                                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">{variant.type}</span>
                            </div>
                            <div className="flex items-center gap-1 text-emerald-400">
                                <Sparkles className="w-3 h-3" />
                                <span className="text-[10px] font-bold">{Math.round(variant.predicted_performance * 100)}%</span>
                            </div>
                        </div>

                        <p className="text-xs text-white font-medium mb-2 leading-relaxed">
                            {variant.content.title || variant.content.hook_text || variant.content.description}
                        </p>

                        <div className="flex items-center justify-between pt-2 border-t border-white/5">
                            <p className="text-[10px] text-gray-500 italic pr-4 truncate">
                                {variant.content.implementation}
                            </p>
                            <button className="p-1.5 hover:bg-white/10 rounded transition-colors text-gray-400 hover:text-white">
                                <Copy className="w-3 h-3" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {result.rationale && (
                <div className="mt-4 p-3 bg-brand-violet/5 rounded-lg border border-brand-violet/10">
                    <p className="text-[10px] font-bold text-brand-violet uppercase mb-1">Agent Rationale</p>
                    <p className="text-[11px] text-gray-400 leading-relaxed italic">
                        &quot;{result.rationale}&quot;
                    </p>
                </div>
            )}
        </div>
    );
}
