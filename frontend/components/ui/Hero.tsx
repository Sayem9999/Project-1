'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function Hero() {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const features = [
        { icon: '⚡', text: '10 AI Agents' },
        { icon: '🎬', text: 'Cinematic Effects' },
        { icon: '✨', text: 'Auto Transitions' },
    ];

    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-[#0a0a0f]">
                {/* Gradient Orbs */}
                <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-cyan-500/20 rounded-full blur-[120px] animate-pulse" />
                <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-violet-500/20 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '1s' }} />

                {/* Grid Pattern */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:60px_60px]" />
            </div>

            <div className="container relative z-10 px-6 py-32">
                <div className={`max-w-4xl mx-auto text-center transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
                    {/* Badge */}
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/10 to-violet-500/10 border border-cyan-500/20 mb-8">
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                        <span className="text-sm text-cyan-400 font-medium">Powered by 10 AI Agents</span>
                    </div>

                    {/* Headline */}
                    <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
                        <span className="text-white">Transform Videos with</span>
                        <br />
                        <span className="bg-gradient-to-r from-cyan-400 via-violet-400 to-pink-400 bg-clip-text text-transparent">
                            AI-Powered Magic
                        </span>
                    </h1>

                    {/* Subheadline */}
                    <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
                        Upload your raw footage and let our AI studio crew—Director, Colorist,
                        VFX Artist & more—create cinematic content automatically.
                    </p>

                    {/* Feature Pills */}
                    <div className="flex flex-wrap justify-center gap-3 mb-10">
                        {features.map((feature, i) => (
                            <div
                                key={i}
                                className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-gray-300"
                                style={{ animationDelay: `${i * 0.1}s` }}
                            >
                                <span>{feature.icon}</span>
                                <span>{feature.text}</span>
                            </div>
                        ))}
                    </div>

                    {/* CTA Buttons */}
                    <div className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
                        <Link
                            href="/signup"
                            className="group relative px-8 py-4 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-xl text-lg font-semibold text-white overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_40px_rgba(0,212,255,0.4)]"
                        >
                            <span className="relative z-10 flex items-center justify-center gap-2">
                                Start Editing Free
                                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                                </svg>
                            </span>
                        </Link>
                        <Link
                            href="/#demo"
                            className="px-8 py-4 rounded-xl text-lg font-semibold text-white border border-white/20 hover:bg-white/5 transition-all flex items-center justify-center gap-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Watch Demo
                        </Link>
                    </div>

                    {/* Trust Badges */}
                    <div className="flex flex-col items-center gap-4">
                        <p className="text-sm text-gray-500">Trusted by creators worldwide</p>
                        <div className="flex items-center gap-6">
                            <div className="flex -space-x-2">
                                {[1, 2, 3, 4, 5].map((i) => (
                                    <div key={i} className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 border-2 border-[#0a0a0f] flex items-center justify-center text-xs font-bold text-white">
                                        {String.fromCharCode(64 + i)}
                                    </div>
                                ))}
                            </div>
                            <div className="text-left">
                                <div className="flex items-center gap-1 text-yellow-400">
                                    {[1, 2, 3, 4, 5].map((i) => (
                                        <svg key={i} className="w-4 h-4 fill-current" viewBox="0 0 20 20">
                                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                        </svg>
                                    ))}
                                </div>
                                <p className="text-xs text-gray-500">4.9/5 from 500+ reviews</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Floating Elements */}
                <div className="absolute top-20 left-10 w-20 h-20 rounded-xl bg-gradient-to-br from-cyan-500/20 to-transparent border border-cyan-500/20 backdrop-blur-sm animate-float hidden lg:block" />
                <div className="absolute bottom-32 right-10 w-16 h-16 rounded-xl bg-gradient-to-br from-violet-500/20 to-transparent border border-violet-500/20 backdrop-blur-sm animate-float hidden lg:block" style={{ animationDelay: '0.5s' }} />
            </div>

            {/* Bottom Gradient Fade */}
            <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0a0a0f] to-transparent" />
        </section>
    );
}
