export default function Features() {
    const features = [
        {
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
            ),
            title: 'AI Director',
            description: 'MAX analyzes your footage and creates a cinematic editing strategy.',
            color: 'cyan',
        },
        {
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243 4.243 3 3 0 004.243-4.243zm0-5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z" />
                </svg>
            ),
            title: 'Smart Cuts',
            description: 'Precision editing that keeps the best moments and removes the rest.',
            color: 'violet',
        },
        {
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
            ),
            title: 'Color Grading',
            description: 'Hollywood-grade color correction tailored to your video\'s mood.',
            color: 'pink',
        },
        {
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
            ),
            title: 'Visual Effects',
            description: 'NOVA adds vignettes, film grain, and cinematic effects automatically.',
            color: 'amber',
        },
        {
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
            ),
            title: 'Transitions',
            description: 'Smooth, cinematic transitions between scenes—fades, wipes, and more.',
            color: 'emerald',
        },
        {
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
            ),
            title: 'Auto Thumbnails',
            description: 'THUMB finds the perfect frame and enhances it for maximum clicks.',
            color: 'rose',
        },
    ];

    const colorClasses: Record<string, { bg: string; border: string; text: string; glow: string }> = {
        cyan: { bg: 'bg-cyan-500/10', border: 'border-cyan-500/30', text: 'text-cyan-400', glow: 'group-hover:shadow-[0_0_30px_rgba(0,212,255,0.3)]' },
        violet: { bg: 'bg-violet-500/10', border: 'border-violet-500/30', text: 'text-violet-400', glow: 'group-hover:shadow-[0_0_30px_rgba(139,92,246,0.3)]' },
        pink: { bg: 'bg-pink-500/10', border: 'border-pink-500/30', text: 'text-pink-400', glow: 'group-hover:shadow-[0_0_30px_rgba(236,72,153,0.3)]' },
        amber: { bg: 'bg-amber-500/10', border: 'border-amber-500/30', text: 'text-amber-400', glow: 'group-hover:shadow-[0_0_30px_rgba(245,158,11,0.3)]' },
        emerald: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', glow: 'group-hover:shadow-[0_0_30px_rgba(16,185,129,0.3)]' },
        rose: { bg: 'bg-rose-500/10', border: 'border-rose-500/30', text: 'text-rose-400', glow: 'group-hover:shadow-[0_0_30px_rgba(244,63,94,0.3)]' },
    };

    return (
        <section id="features" className="py-24 relative">
            <div className="container mx-auto px-6">
                {/* Section Header */}
                <div className="text-center mb-16">
                    <span className="inline-block px-4 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-sm font-medium mb-4">
                        Features
                    </span>
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                        Your AI Video Crew
                    </h2>
                    <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                        10 specialized AI agents work together to transform your raw footage into polished, professional content.
                    </p>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {features.map((feature, i) => {
                        const colors = colorClasses[feature.color];
                        return (
                            <div
                                key={i}
                                className={`group relative p-6 rounded-2xl bg-[#12121a] border border-white/5 transition-all duration-300 hover:-translate-y-1 ${colors.glow}`}
                            >
                                {/* Icon */}
                                <div className={`w-12 h-12 rounded-xl ${colors.bg} ${colors.border} border flex items-center justify-center mb-4 ${colors.text}`}>
                                    {feature.icon}
                                </div>

                                {/* Content */}
                                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                                <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>

                                {/* Hover Gradient */}
                                <div className={`absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none ${colors.bg}`} style={{ filter: 'blur(40px)' }} />
                            </div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
}
