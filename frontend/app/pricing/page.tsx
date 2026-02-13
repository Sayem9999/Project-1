'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Check, ArrowLeft, Star, CreditCard, Zap, Shield, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { apiRequest, ApiError, clearAuth } from '@/lib/api';
import Link from 'next/link';
import { toast } from 'sonner';

export default function PricingPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        setIsLoggedIn(!!localStorage.getItem('token'));
    }, []);

    const handlePurchase = async () => {
        setLoading(true);
        try {
            const data = await apiRequest<{ url?: string }>('/payments/create-checkout-session', {
                method: 'POST',
                auth: true
            });
            if (data.url) {
                window.location.href = data.url;
            } else {
                toast.error('Checkout initialization failed');
            }
        } catch (error) {
            if (error instanceof ApiError && error.isAuth) {
                clearAuth();
                router.push('/login?redirect=/pricing');
                return;
            }
            console.error('Purchase error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-obsidian-950 text-white selection:bg-brand-cyan/30 overflow-hidden">
            {/* Ambient Background */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[80vw] h-[80vw] bg-brand-cyan/5 rounded-full blur-[120px] animate-pulse-slow" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[80vw] h-[80vw] bg-brand-violet/5 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
                <div className="absolute inset-0 bg-grid-pattern opacity-10" />
            </div>

            {/* Navigation Header */}
            <div className="relative z-20 flex items-center justify-between p-6 md:p-10">
                <Link href={isLoggedIn ? "/dashboard" : "/"} className="flex items-center gap-3 text-gray-500 hover:text-white transition-all group">
                    <div className="p-2.5 rounded-xl bg-white/5 border border-white/5 group-hover:bg-white/10 transition-colors">
                        <ArrowLeft className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-black uppercase tracking-[0.3em] hidden sm:block">Return To Lab</span>
                </Link>

                <div className="flex items-center gap-3">
                    <Shield className="w-4 h-4 text-emerald-400" />
                    <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Encrypted Checkout Active</span>
                </div>
            </div>

            <main className="relative z-10 max-w-6xl mx-auto px-6 pt-12 pb-32">
                <div className="text-center mb-16 md:mb-24 animate-in fade-in slide-in-from-bottom-4 duration-1000">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-cyan/10 border border-brand-cyan/20 text-[10px] font-black uppercase tracking-widest text-brand-cyan mb-8">
                        <Star className="w-3 h-3 fill-brand-cyan" />
                        <span>Exclusive Operator Access</span>
                    </div>
                    <h1 className="text-4xl md:text-6xl font-black tracking-tighter text-white mb-6">
                        Scale Your <span className="bg-gradient-to-r from-brand-cyan to-brand-violet bg-clip-text text-transparent italic">Production.</span>
                    </h1>
                    <p className="text-gray-500 max-w-2xl mx-auto text-lg font-bold leading-relaxed">
                        Fuel your creativity with high-octane credits for the Hollywood Pipeline (v4.0). Priority rendering. Zero watermarks. Infinite impact.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch max-w-4xl mx-auto">
                    {/* Starter Tier */}
                    <div className="glass-panel p-10 rounded-[40px] border-white/5 relative overflow-hidden group hover:border-white/10 transition-colors">
                        <div className="mb-10">
                            <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em] mb-2">Tier: Standard</h3>
                            <div className="flex items-baseline gap-2">
                                <span className="text-4xl font-black text-white">$0</span>
                                <span className="text-[10px] font-black text-gray-600 uppercase tracking-widest">/ Monthly Quota</span>
                            </div>
                        </div>

                        <ul className="space-y-6 mb-12">
                            {[
                                "Standard Pipeline Access (v3)",
                                "Basic Media Processing",
                                "Community Support",
                                "Watermarked Exports"
                            ].map((feature, i) => (
                                <li key={i} className="flex gap-4 items-center group/item">
                                    <div className="w-6 h-6 rounded-lg bg-white/5 flex items-center justify-center text-gray-500 group-hover/item:text-brand-cyan transition-colors">
                                        <Check size={14} />
                                    </div>
                                    <span className="text-sm font-bold text-gray-500 group-hover/item:text-gray-300 transition-colors">{feature}</span>
                                </li>
                            ))}
                        </ul>

                        <Link href="/signup">
                            <Button variant="secondary" className="w-full h-14 font-black text-[10px] uppercase tracking-[0.2em]">
                                Free Allocation Active
                            </Button>
                        </Link>
                    </div>

                    {/* Pro Tier */}
                    <div className="glass-panel p-10 rounded-[40px] border-brand-cyan/30 bg-gradient-to-br from-brand-cyan/5 to-transparent relative overflow-hidden shadow-2xl shadow-brand-cyan/10">
                        <div className="absolute top-0 right-0 p-4">
                            <div className="bg-brand-cyan text-black text-[10px] font-black px-4 py-1.5 rounded-full uppercase tracking-tighter">
                                DEPLOY_NOW
                            </div>
                        </div>

                        <div className="mb-10">
                            <h3 className="text-[10px] font-black text-brand-cyan uppercase tracking-[0.3em] mb-2">Tier: Professional</h3>
                            <div className="flex items-baseline gap-2">
                                <span className="text-4xl font-black text-white">$10</span>
                                <span className="text-[10px] font-black text-brand-cyan/60 uppercase tracking-widest">/ 10 CREDITS</span>
                            </div>
                        </div>

                        <ul className="space-y-6 mb-12">
                            {[
                                "Hollywood Pipeline (v4.0)",
                                "5 Pro Edits (2 Credits/each)",
                                "No Watermark Exports",
                                "Priority Thread Allocation",
                                "Intelligence Sub-Agents"
                            ].map((feature, i) => (
                                <li key={i} className="flex gap-4 items-center">
                                    <div className="w-6 h-6 rounded-lg bg-brand-cyan/20 flex items-center justify-center text-brand-cyan">
                                        <Check size={14} />
                                    </div>
                                    <span className="text-sm font-black text-white uppercase tracking-tight">{feature}</span>
                                </li>
                            ))}
                        </ul>

                        <div className="space-y-4">
                            <Button
                                onClick={handlePurchase}
                                loading={loading}
                                variant="glow"
                                className="w-full h-16 font-black text-xs uppercase tracking-[0.3em]"
                            >
                                <Zap className="w-4 h-4 mr-2 fill-current" />
                                Initialize Pro Pack
                            </Button>
                            <div className="flex items-center justify-center gap-4 text-[10px] font-black text-gray-600 uppercase tracking-widest">
                                <span className="flex items-center gap-1"><CreditCard className="w-3 h-3" /> Stripe Secure</span>
                                <span className="flex items-center gap-1"><Sparkles className="w-3 h-3" /> Auto-Sync</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* FAQ / Trust Signals */}
                <div className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-12 text-center">
                    <div className="space-y-4">
                        <div className="w-12 h-12 rounded-2xl bg-white/5 mx-auto flex items-center justify-center text-brand-cyan">
                            <CreditCard className="w-6 h-6" />
                        </div>
                        <h4 className="text-xs font-black uppercase tracking-widest text-white">No Subscription</h4>
                        <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest leading-loose">One-time credit packs. No hidden recurring fees. Pay as you produce.</p>
                    </div>
                    <div className="space-y-4">
                        <div className="w-12 h-12 rounded-2xl bg-white/5 mx-auto flex items-center justify-center text-brand-violet">
                            <Zap className="w-6 h-6" />
                        </div>
                        <h4 className="text-xs font-black uppercase tracking-widest text-white">Instant Sync</h4>
                        <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest leading-loose">Credits are allocated to your identity immediately after confirmation.</p>
                    </div>
                    <div className="space-y-4">
                        <div className="w-12 h-12 rounded-2xl bg-white/5 mx-auto flex items-center justify-center text-emerald-400">
                            <Shield className="w-6 h-6" />
                        </div>
                        <h4 className="text-xs font-black uppercase tracking-widest text-white">Corporate Grade</h4>
                        <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest leading-loose">Enterprise level security protocols protect every transaction.</p>
                    </div>
                </div>
            </main>
        </div>
    );
}
