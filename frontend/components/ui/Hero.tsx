import Link from 'next/link';

export function Hero() {
    return (
        <div className="relative isolate pt-14">
            {/* Background Gradients */}
            <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
                <div
                    className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-brand-cyan to-brand-violet opacity-20 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
                    style={{ clipPath: 'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)' }}
                />
            </div>

            <div className="py-24 sm:py-32 lg:pb-40">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-4xl text-center">
                        {/* Trust Badge */}
                        <div className="mb-6 animate-slide-up">
                            <span className="inline-flex items-center gap-2 rounded-full bg-brand-cyan/10 px-4 py-1.5 text-sm text-brand-cyan ring-1 ring-inset ring-brand-cyan/20">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-cyan opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-cyan"></span>
                                </span>
                                AI-Powered • 10x Faster Editing
                            </span>
                        </div>

                        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl lg:text-7xl text-glow animate-float">
                            Edit Videos Like a <br />
                            <span className="bg-gradient-to-r from-brand-cyan via-brand-violet to-brand-fuchsia bg-clip-text text-transparent">
                                Hollywood Studio
                            </span>
                        </h1>
                        <p className="mt-6 text-lg leading-8 text-slate-300 max-w-2xl mx-auto">
                            Upload raw footage. Our AI Director, Colorist, and Audio Engineers
                            work together 24/7 to deliver studio-quality edits in minutes.
                        </p>

                        {/* CTA Buttons */}
                        <div className="mt-10 flex items-center justify-center gap-x-6">
                            <Link href="/signup" className="btn-primary btn-glow text-lg px-8 py-4 flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                                Start Free
                            </Link>
                            <Link href="/login" className="group text-sm font-semibold leading-6 text-white hover:text-brand-cyan transition-colors flex items-center gap-1">
                                Already have an account?
                                <span className="group-hover:translate-x-1 transition-transform">→</span>
                            </Link>
                        </div>

                        {/* Social Proof */}
                        <div className="mt-12 flex items-center justify-center gap-8 text-slate-500 text-sm">
                            <div className="flex items-center gap-2">
                                <svg className="w-5 h-5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                No credit card required
                            </div>
                            <div className="flex items-center gap-2">
                                <svg className="w-5 h-5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                5 free renders/month
                            </div>
                        </div>
                    </div>

                    {/* Mockup / Visual */}
                    <div className="mt-16 flow-root sm:mt-24">
                        <div className="glass-panel -m-2 rounded-xl p-2 lg:-m-4 lg:rounded-2xl lg:p-4 card-hover">
                            <div className="rounded-md bg-slate-950/50 shadow-2xl ring-1 ring-white/10 overflow-hidden aspect-video relative group">
                                {/* Dashboard Preview */}
                                <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-950">
                                    {/* Agent Cards Preview */}
                                    <div className="grid grid-cols-3 gap-4 p-8 w-full max-w-2xl opacity-60 group-hover:opacity-100 transition-opacity">
                                        <div className="glass-panel p-4 rounded-lg animate-slide-up" style={{ animationDelay: '0ms' }}>
                                            <div className="w-8 h-8 rounded-full bg-brand-cyan/20 mb-2"></div>
                                            <div className="h-2 bg-slate-700 rounded w-3/4 mb-1"></div>
                                            <div className="h-2 bg-slate-800 rounded w-1/2"></div>
                                        </div>
                                        <div className="glass-panel p-4 rounded-lg animate-slide-up" style={{ animationDelay: '100ms' }}>
                                            <div className="w-8 h-8 rounded-full bg-brand-violet/20 mb-2"></div>
                                            <div className="h-2 bg-slate-700 rounded w-2/3 mb-1"></div>
                                            <div className="h-2 bg-slate-800 rounded w-1/2"></div>
                                        </div>
                                        <div className="glass-panel p-4 rounded-lg animate-slide-up" style={{ animationDelay: '200ms' }}>
                                            <div className="w-8 h-8 rounded-full bg-brand-fuchsia/20 mb-2"></div>
                                            <div className="h-2 bg-slate-700 rounded w-full mb-1"></div>
                                            <div className="h-2 bg-slate-800 rounded w-2/3"></div>
                                        </div>
                                    </div>
                                </div>
                                {/* Scan Line */}
                                <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-brand-cyan via-brand-violet to-brand-fuchsia" style={{ animation: 'shimmer 2s infinite' }}></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
