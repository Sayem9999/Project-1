'use client';

export function HowItWorks() {
    const steps = [
        {
            title: 'Upload Footage',
            desc: 'Drag & drop your raw video files. We support MP4, MOV, and AVI.',
            icon: (
                <svg className="w-8 h-8 text-brand-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
            )
        },
        {
            title: 'AI Director Planning',
            desc: 'Our AI analyzes pacing, mood, and content to create a perfect cut.',
            icon: (
                <svg className="w-8 h-8 text-brand-violet" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
            )
        },
        {
            title: 'Auto-Edit & Polish',
            desc: 'We cut silence, grade colors, and mix audio in seconds.',
            icon: (
                <svg className="w-8 h-8 text-brand-fuchsia" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
            )
        }
    ];

    return (
        <section className="py-24 relative overflow-hidden">
            <div className="absolute inset-0 bg-slate-950/50 skew-y-3 transform origin-top-left -z-10 h-full w-full"></div>

            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl text-glow">
                        From Raw to Viral in 3 Steps
                    </h2>
                    <p className="mt-4 text-lg text-slate-400">
                        Automate the boring parts of video editing.
                    </p>
                </div>

                <div className="grid grid-cols-1 gap-12 md:grid-cols-3">
                    {steps.map((step, i) => (
                        <div key={i} className="relative group">
                            <div className="absolute -inset-0.5 bg-gradient-to-r from-brand-cyan to-brand-violet rounded-2xl blur opacity-25 group-hover:opacity-10 transition duration-1000"></div>
                            <div className="relative p-8 bg-slate-900 rounded-2xl border border-slate-800 hover:border-slate-700 transition-all text-center">
                                <div className="inline-flex items-center justify-center p-3 bg-slate-800 rounded-xl mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                                    {step.icon}
                                </div>
                                <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                                <p className="text-slate-400 leading-relaxed">{step.desc}</p>

                                {/* Connector Line (Desktop) */}
                                {i !== 2 && (
                                    <div className="hidden md:block absolute top-1/2 -right-6 w-12 h-0.5 bg-gradient-to-r from-slate-800 to-transparent"></div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
