export function FeatureGrid() {
    const features = [
        {
            title: 'AI Director',
            description: 'Our advanced AI analyzes your footage to understand context, pacing, and emotion, acting as a creative lead.',
            icon: (
                <svg className="h-6 w-6 text-brand-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
            ),
        },
        {
            title: 'Smart Cutting',
            description: 'Automatically removes silence, fillers, and awkward pauses while maintaining a natural, broadcast-quality flow.',
            icon: (
                <svg className="h-6 w-6 text-brand-violet" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243 4.243 3 3 0 004.243-4.243zm0 0L2.802 9.006" />
                </svg>
            ),
        },
        {
            title: 'Pro Color & Audio',
            description: 'Instant professional color grading and audio mastering. Your video will look and sound like a high-budget production.',
            icon: (
                <svg className="h-6 w-6 text-brand-fuchsia" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
            ),
        },
    ];

    return (
        <div id="features" className="py-24 sm:py-32">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
                <div className="mx-auto max-w-2xl text-center">
                    <h2 className="text-base font-semibold leading-7 text-brand-cyan">Everything you need</h2>
                    <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl text-glow">
                        Your personal post-production team
                    </p>
                    <p className="mt-6 text-lg leading-8 text-slate-400">
                        Stop spending hours in Premiere Pro. Let our AI team handle the technical details while you focus on creating.
                    </p>
                </div>
                <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
                    <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
                        {features.map((feature) => (
                            <div key={feature.title} className="glass-panel p-8 rounded-2xl relative group hover:-translate-y-2">
                                <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-brand-cyan/5 to-brand-violet/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl pointer-events-none"></div>
                                <dt className="flex items-center gap-x-3 text-base font-bold leading-7 text-white">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 border border-slate-800 group-hover:border-brand-cyan/50 transition-colors">
                                        {feature.icon}
                                    </div>
                                    {feature.title}
                                </dt>
                                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-slate-400">
                                    <p className="flex-auto">{feature.description}</p>
                                </dd>
                            </div>
                        ))}
                    </dl>
                </div>
            </div>
        </div>
    );
}
