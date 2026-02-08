'use client';

interface DirectorPanelProps {
    pacing: string;
    setPacing: (v: string) => void;
    mood: string;
    setMood: (v: string) => void;
    ratio: string;
    setRatio: (v: string) => void;
}

export function DirectorPanel({ pacing, setPacing, mood, setMood, ratio, setRatio }: DirectorPanelProps) {
    const pacingOptions = [
        { value: 'fast', label: 'Fast (TikTok)', desc: 'Quick cuts, high energy' },
        { value: 'medium', label: 'Medium (YouTube)', desc: 'Natural, balanced flow' },
        { value: 'slow', label: 'Slow (Docu)', desc: 'Cinematic, thoughtful pauses' },
    ];

    const moodOptions = [
        { value: 'professional', label: 'Professional', desc: 'Clean, corporate, trusted' },
        { value: 'cinematic', label: 'Cinematic', desc: 'Dramatic lighting, moody' },
        { value: 'energetic', label: 'Energetic', desc: 'Bright, loud, hype' },
    ];

    const ratioOptions = [
        { value: '16:9', label: 'Landscape (16:9)', desc: 'YouTube, TV' },
        { value: '9:16', label: 'Vertical (9:16)', desc: 'Shorts, TikTok, Reels' },
    ];

    return (
        <div className="space-y-6 animate-shimmer bg-gradient-to-br from-white/5 to-white/[0.02] p-6 rounded-xl border border-white/10">
            <div className="flex items-center gap-2 mb-4">
                <div className="h-2 w-2 rounded-full bg-brand-cyan animate-pulse"></div>
                <h3 className="text-lg font-semibold text-white">Director's Controls</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Pacing */}
                <div className="space-y-3">
                    <label className="text-sm font-medium text-slate-400">Pacing Strategy</label>
                    <div className="space-y-2">
                        {pacingOptions.map((opt) => (
                            <button
                                key={opt.value}
                                type="button"
                                onClick={() => setPacing(opt.value)}
                                className={`w-full text-left p-3 rounded-lg border transition-all duration-200 ${pacing === opt.value
                                        ? 'bg-brand-cyan/20 border-brand-cyan text-white shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                                        : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-600'
                                    }`}
                            >
                                <div className="font-medium text-sm">{opt.label}</div>
                                <div className="text-xs opacity-70">{opt.desc}</div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Mood */}
                <div className="space-y-3">
                    <label className="text-sm font-medium text-slate-400">Atmosphere & Mood</label>
                    <div className="space-y-2">
                        {moodOptions.map((opt) => (
                            <button
                                key={opt.value}
                                type="button"
                                onClick={() => setMood(opt.value)}
                                className={`w-full text-left p-3 rounded-lg border transition-all duration-200 ${mood === opt.value
                                        ? 'bg-brand-violet/20 border-brand-violet text-white shadow-[0_0_15px_rgba(139,92,246,0.2)]'
                                        : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-600'
                                    }`}
                            >
                                <div className="font-medium text-sm">{opt.label}</div>
                                <div className="text-xs opacity-70">{opt.desc}</div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Ratio */}
                <div className="space-y-3">
                    <label className="text-sm font-medium text-slate-400">Aspect Ratio</label>
                    <div className="space-y-2">
                        {ratioOptions.map((opt) => (
                            <button
                                key={opt.value}
                                type="button"
                                onClick={() => setRatio(opt.value)}
                                className={`w-full text-left p-3 rounded-lg border transition-all duration-200 ${ratio === opt.value
                                        ? 'bg-brand-fuchsia/20 border-brand-fuchsia text-white shadow-[0_0_15px_rgba(217,70,239,0.2)]'
                                        : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-600'
                                    }`}
                            >
                                <div className="font-medium text-sm">{opt.label}</div>
                                <div className="text-xs opacity-70">{opt.desc}</div>
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
