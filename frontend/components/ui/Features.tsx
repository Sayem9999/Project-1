export default function Features() {
    const features = [
        {
            icon: '🎬',
            title: 'AI Director',
            description: 'MAX orchestrates your entire edit, making creative decisions like a pro.',
            gradient: 'from-cyan-500 to-blue-500',
        },
        {
            icon: '✂️',
            title: 'Smart Cuts',
            description: 'Automatic scene detection and precision cutting for perfect pacing.',
            gradient: 'from-violet-500 to-purple-500',
        },
        {
            icon: '🎨',
            title: 'Color Grading',
            description: 'Cinema-quality color correction that matches your mood.',
            gradient: 'from-pink-500 to-rose-500',
        },
        {
            icon: '✨',
            title: 'Visual Effects',
            description: 'NOVA adds vignettes, film grain, and cinematic polish.',
            gradient: 'from-amber-500 to-orange-500',
        },
        {
            icon: '🔀',
            title: 'Transitions',
            description: 'Smooth, professional transitions between every scene.',
            gradient: 'from-emerald-500 to-green-500',
        },
        {
            icon: '📸',
            title: 'Thumbnails',
            description: 'AI-generated click-worthy thumbnails for maximum engagement.',
            gradient: 'from-blue-500 to-indigo-500',
        },
    ];

    return (
        <section id="features" className="py-32 bg-black relative overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-violet-500/10 rounded-full blur-[150px]" />
            </div>

            <div className="relative z-10 max-w-6xl mx-auto px-6">
                {/* Header */}
                <div className="text-center mb-20">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-6">
                        <span className="text-sm text-gray-300">Powered by AI</span>
                    </div>
                    <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
                        Your AI video crew
                    </h2>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                        10 specialized agents work together to transform your raw footage into polished content.
                    </p>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {features.map((feature, i) => (
                        <div
                            key={i}
                            className="group relative p-8 rounded-3xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all duration-500 hover:-translate-y-1"
                        >
                            {/* Hover Glow */}
                            <div className={`absolute inset-0 rounded-3xl bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                            {/* Icon */}
                            <div className="text-4xl mb-6">{feature.icon}</div>

                            {/* Content */}
                            <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                            <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
