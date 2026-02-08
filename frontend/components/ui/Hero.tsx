'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function Hero() {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-black">
            {/* Animated Background */}
            <div className="absolute inset-0">
                {/* Gradient Mesh */}
                <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-cyan-500/20 rounded-full blur-[150px] animate-pulse" />
                <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-violet-500/20 rounded-full blur-[150px] animate-pulse" style={{ animationDelay: '1s' }} />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-pink-500/10 rounded-full blur-[100px]" />

                {/* Noise Texture */}
                <div className="absolute inset-0 opacity-30" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 256 256\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noise\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noise)\'/%3E%3C/svg%3E")' }} />

                {/* Grid */}
                <div className="absolute inset-0" style={{
                    backgroundImage: 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)',
                    backgroundSize: '100px 100px'
                }} />
            </div>

            <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
                <div className={`transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
                    {/* Badge */}
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-sm">
                        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="text-sm text-gray-300">Now with 10 AI Agents</span>
                        <span className="text-xs text-gray-500">→</span>
                    </div>

                    {/* Main Headline */}
                    <h1 className="text-6xl md:text-8xl font-bold tracking-tight mb-6">
                        <span className="text-white">Edit videos</span>
                        <br />
                        <span className="bg-gradient-to-r from-cyan-400 via-violet-400 to-pink-400 bg-clip-text text-transparent">
                            with AI magic
                        </span>
                    </h1>

                    {/* Subheadline */}
                    <p className="text-xl md:text-2xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
                        Upload raw footage. Our AI crew handles the cuts, color grading, transitions, and effects. Get cinema-ready videos in minutes.
                    </p>

                    {/* CTA Buttons */}
                    <div className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
                        <Link
                            href="/signup"
                            className="group relative px-8 py-4 rounded-full bg-white text-black text-lg font-semibold overflow-hidden transition-all hover:shadow-[0_0_50px_rgba(255,255,255,0.3)]"
                        >
                            <span className="relative z-10 flex items-center justify-center gap-2">
                                Start for free
                                <span className="group-hover:translate-x-1 transition-transform">→</span>
                            </span>
                        </Link>
                        <Link
                            href="/#demo"
                            className="px-8 py-4 rounded-full text-lg font-medium text-white border border-white/20 hover:bg-white/5 transition-all flex items-center justify-center gap-2"
                        >
                            <span className="text-xl">▶</span>
                            Watch demo
                        </Link>
                    </div>

                    {/* Stats */}
                    <div className="flex flex-wrap justify-center gap-8 md:gap-16">
                        {[
                            { value: '10K+', label: 'Videos created' },
                            { value: '4.9★', label: 'User rating' },
                            { value: '10', label: 'AI agents' },
                        ].map((stat, i) => (
                            <div key={i} className="text-center">
                                <div className="text-3xl md:text-4xl font-bold text-white mb-1">{stat.value}</div>
                                <div className="text-sm text-gray-500">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Preview Card - Floating */}
            <div className={`absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-4xl px-6 transition-all duration-1000 delay-500 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-20'}`}>
                <div className="relative bg-gradient-to-b from-white/5 to-transparent rounded-t-3xl border border-white/10 border-b-0 p-1 backdrop-blur-sm">
                    <div className="bg-black/50 rounded-t-[20px] p-4 flex items-center gap-3">
                        <div className="flex gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-500" />
                            <div className="w-3 h-3 rounded-full bg-yellow-500" />
                            <div className="w-3 h-3 rounded-full bg-green-500" />
                        </div>
                        <div className="flex-1 text-center text-sm text-gray-500">Proedit Studio</div>
                    </div>
                    <div className="h-20 bg-gradient-to-b from-black/50 to-transparent" />
                </div>
            </div>

            {/* Scroll Indicator */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 hidden md:flex flex-col items-center gap-2 text-gray-500">
                <span className="text-xs uppercase tracking-widest">Scroll</span>
                <div className="w-5 h-8 rounded-full border border-white/20 flex items-start justify-center p-1">
                    <div className="w-1 h-2 rounded-full bg-white/50 animate-bounce" />
                </div>
            </div>
        </section>
    );
}
