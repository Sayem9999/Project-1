'use client';

import { useState } from 'react';

type Theme = 'professional' | 'viral' | 'cinematic' | 'minimalist' | 'documentary';

const THEMES: { id: Theme; label: string; description: string; color: string }[] = [
    { id: 'professional', label: 'Professional', description: 'Clean cuts, authoritative pacing, standard transitions.', color: 'bg-blue-500' },
    { id: 'viral', label: 'Viral / TikTok', description: 'Fast-paced, jump cuts, hook-focused structure.', color: 'bg-brand-magenta' },
    { id: 'cinematic', label: 'Cinematic', description: 'Slow pacing, wide shots, dramatic music and coloring.', color: 'bg-brand-violet' },
    { id: 'minimalist', label: 'Minimalist', description: 'Sparse editing, focus on audio and essential visuals.', color: 'bg-slate-400' },
    { id: 'documentary', label: 'Documentary', description: 'Narrative-driven, b-roll heavy, journalistic style.', color: 'bg-emerald-500' },
];

export function ThemeSelector({ value, onChange }: { value: string; onChange: (v: string) => void }) {
    return (
        <div className="space-y-3">
            <label className="text-sm font-medium text-slate-400">Editing Style</label>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {THEMES.map((theme) => (
                    <button
                        key={theme.id}
                        type="button"
                        onClick={() => onChange(theme.id)}
                        className={`group relative flex items-start space-x-3 rounded-lg border p-4 text-left transition-all hover:border-brand-cyan/50 ${value === theme.id
                                ? 'border-brand-cyan bg-brand-cyan/10 ring-1 ring-brand-cyan/20'
                                : 'border-slate-800 bg-slate-900/50 hover:bg-slate-900'
                            }`}
                    >
                        <div className={`mt-1 h-2 w-2 rounded-full ${theme.color} shadow-[0_0_8px_currentColor]`} />
                        <div>
                            <div className="font-semibold text-slate-200 group-hover:text-brand-cyan">{theme.label}</div>
                            <div className="mt-1 text-xs text-slate-500">{theme.description}</div>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}
