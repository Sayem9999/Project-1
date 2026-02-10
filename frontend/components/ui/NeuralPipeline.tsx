'use client';
import { motion } from 'framer-motion';
import { Brain, Zap, Wand2, Shield, Activity } from 'lucide-react';

export default function NeuralPipeline() {
    const steps = [
        { icon: Brain, label: 'Strategy', color: 'text-brand-cyan', delay: 0 },
        { icon: Zap, label: 'Analysis', color: 'text-brand-violet', delay: 1 },
        { icon: Wand2, label: 'Creative', color: 'text-brand-fuchsia', delay: 2 },
        { icon: activity, label: 'QC Post', color: 'text-emerald-400', delay: 3 },
    ];

    return (
        <div className="relative w-full h-full flex items-center justify-center p-8 lg:p-12 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-brand-cyan/5 via-transparent to-brand-violet/5 animate-pulse-slow" />

            {/* Dynamic Pulse Ring */}
            <motion.div
                animate={{ scale: [1, 1.2, 1], opacity: [0.1, 0.2, 0.1] }}
                transition={{ duration: 4, repeat: Infinity }}
                className="absolute inset-0 border-[40px] border-white/5 rounded-full"
            />

            <div className="relative z-10 w-full max-w-2xl space-y-8">
                <div className="flex items-center justify-between gap-4">
                    {steps.map((Step, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: Step.delay * 0.2 }}
                            className="flex flex-col items-center gap-3 group"
                        >
                            <div className={`p-4 rounded-2xl bg-white/5 border border-white/10 ${Step.color} group-hover:scale-110 transition-transform duration-500 shadow-xl group-hover:shadow-${Step.color.split('-')[1]}/20`}>
                                <Step.icon className="w-6 h-6 lg:w-8 lg:h-8" />
                            </div>
                            <span className="text-[10px] lg:text-xs font-bold uppercase tracking-widest text-gray-500 group-hover:text-white transition-colors">
                                {Step.label}
                            </span>
                        </motion.div>
                    ))}
                </div>

                {/* Neural Connections Visual */}
                <div className="relative h-2 bg-white/5 rounded-full overflow-hidden border border-white/5">
                    <motion.div
                        animate={{ x: ['100%', '-100%'] }}
                        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-0 w-1/2 bg-gradient-to-r from-transparent via-brand-cyan/40 to-transparent"
                    />
                    <motion.div
                        animate={{ x: ['-100%', '100%'] }}
                        transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-0 w-1/3 bg-gradient-to-r from-transparent via-brand-violet/40 to-transparent"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="glass-card p-4 rounded-2xl border-white/5 space-y-2">
                        <div className="flex items-center justify-between text-[10px] text-gray-500 uppercase font-bold tracking-tighter">
                            <span>Agent Throughput</span>
                            <span className="text-brand-cyan">Active</span>
                        </div>
                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                            <motion.div
                                animate={{ width: ['20%', '80%', '60%', '95%'] }}
                                transition={{ duration: 8, repeat: Infinity }}
                                className="h-full bg-brand-cyan"
                            />
                        </div>
                    </div>
                    <div className="glass-card p-4 rounded-2xl border-white/5 space-y-2">
                        <div className="flex items-center justify-between text-[10px] text-gray-500 uppercase font-bold tracking-tighter">
                            <span>QC Scoring</span>
                            <span className="text-emerald-400">9.8/10</span>
                        </div>
                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                            <motion.div
                                animate={{ width: ['90%', '98%', '95%', '99%'] }}
                                transition={{ duration: 4, repeat: Infinity }}
                                className="h-full bg-emerald-400"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

const activity = Activity; // Alias for steps
