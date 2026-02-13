'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Play, Sparkles, Wand2, Zap, Layers } from 'lucide-react';
import { Button } from './Button';

const stats = [
    { label: 'AI Edits', value: '1.2M+', icon: Zap },
    { label: 'Creators', value: '45K+', icon: Layers },
    { label: 'Avg Time', value: '3m', icon: ClockIcon },
    { label: 'Efficiency', value: '98%', icon: ActivityIcon },
];

function ClockIcon({ className }: { className?: string }) {
    return <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>;
}

function ActivityIcon({ className }: { className?: string }) {
    return <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>;
}

export default function Hero() {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    if (!isMounted) return null;

    return (
        <section className="relative min-h-[90vh] flex items-center justify-center pt-32 pb-20 overflow-hidden">
            {/* Ambient Background Engine */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-brand-cyan/10 rounded-full blur-[120px] animate-drift-orb" />
                <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-brand-violet/10 rounded-full blur-[100px] animate-drift-orb" style={{ animationDelay: '-9s' }} />
                <div className="absolute inset-0 bg-grid-white/5 bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_at_center,black_70%,transparent_100%)]" />
            </div>

            <div className="container mx-auto px-4 relative z-10">
                <div className="max-w-5xl mx-auto text-center">
                    {/* Badge */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5 }}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-sm border-white/10 text-brand-cyan text-xs font-bold tracking-widest uppercase mb-8 shadow-xl"
                    >
                        <Sparkles className="w-3.5 h-3.5" />
                        Next-Gen Video Intelligence
                    </motion.div>

                    {/* Main Headline */}
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                        className="text-5xl md:text-8xl font-black tracking-tight mb-6 leading-[1.05]"
                    >
                        <span className="text-white">Edit videos</span>
                        <br />
                        <span className="bg-gradient-to-r from-cyan-400 via-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
                            with AI magic
                        </span>
                    </motion.h1>

                    {/* Subheadline */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4, duration: 0.8 }}
                        className="text-lg md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed px-4"
                    >
                        Proedit.ai transforms raw clips into polished social-ready content. Our specialist agents handle the storytelling, transitions, and color science—instantly.
                    </motion.p>

                    {/* CTA Buttons */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6, duration: 0.8 }}
                        className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20 px-4"
                    >
                        <Link href="/dashboard" className="w-full sm:w-auto">
                            <Button variant="glow" size="lg" className="w-full h-16 text-lg group shadow-2xl">
                                Start Creating Free
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </Button>
                        </Link>
                        <Button variant="secondary" size="lg" className="w-full sm:w-auto h-16 text-lg glass-md hover:bg-white/10 transition-all">
                            <Play className="w-5 h-5 mr-1" />
                            Watch Showreel
                        </Button>
                    </motion.div>

                    {/* Stats Highlights */}
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.8, duration: 1 }}
                        className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 max-w-5xl mx-auto"
                    >
                        {stats.map((stat, i) => (
                            <div key={i} className="glass-card p-6 md:p-8 rounded-3xl text-center group relative overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                                <div className="flex justify-center mb-3">
                                    <stat.icon className="w-5 h-5 text-brand-cyan/40 group-hover:text-brand-cyan transition-colors" />
                                </div>
                                <div className="text-3xl md:text-4xl font-black text-white mb-2 tracking-tighter group-hover:scale-110 transition-transform duration-500">
                                    {stat.value}
                                </div>
                                <div className="text-[10px] md:text-xs text-gray-500 uppercase tracking-widest font-black leading-tight">
                                    {stat.label}
                                </div>
                            </div>
                        ))}
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
