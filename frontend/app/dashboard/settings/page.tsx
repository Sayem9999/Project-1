'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { User, Shield, Key, CreditCard, LogOut, ChevronRight, Activity, Sparkles, Monitor } from 'lucide-react';
import { apiRequest, ApiError, clearAuth } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { motion } from 'framer-motion';

interface Me {
    email: string;
    full_name?: string | null;
    credits: number;
    is_admin: boolean;
}

export default function SettingsPage() {
    const router = useRouter();
    const [me, setMe] = useState<Me | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await apiRequest<Me>('/auth/me', { auth: true });
                setMe(data);
            } catch (err) {
                if (err instanceof ApiError && err.isAuth) {
                    clearAuth();
                    router.push('/login');
                    return;
                }
                setError(err instanceof ApiError ? err.message : 'Failed to load settings');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [router]);

    const handleLogout = () => {
        clearAuth();
        router.push('/login');
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh]">
                <div className="w-10 h-10 border-4 border-brand-cyan/20 border-t-brand-cyan rounded-full animate-spin mb-4" />
                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 animate-pulse">Syncing Profile</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-12 pb-20 px-2 md:px-0">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-3">
                        <div className="px-3 py-1 rounded-full bg-brand-cyan/10 border border-brand-cyan/30 text-[10px] font-black uppercase tracking-widest text-brand-cyan">CONFIG_NODE</div>
                        <div className="flex items-center gap-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest">
                            <Activity className="w-3 h-3 text-emerald-400" />
                            Session Established
                        </div>
                    </div>
                    <h1 className="text-4xl font-black tracking-tighter text-white mb-2 uppercase">Account Systems</h1>
                    <p className="text-gray-500 font-bold text-sm tracking-tight">Identity management and administrative governance.</p>
                </div>

                <Button variant="secondary" onClick={handleLogout} className="font-black text-[10px] uppercase tracking-widest border-red-500/20 text-red-400 hover:bg-red-500/10">
                    <LogOut className="w-4 h-4 mr-2" /> Terminante Session
                </Button>
            </div>

            {error && (
                <div className="p-4 rounded-[24px] bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-black uppercase tracking-widest text-center">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Left Column: Profile Card */}
                <div className="md:col-span-1 space-y-6">
                    <div className="glass-panel p-8 rounded-[40px] border-white/5 relative overflow-hidden text-center">
                        <div className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-brand-cyan/10 to-transparent" />
                        <div className="relative z-10">
                            <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-brand-cyan to-brand-violet mx-auto mb-6 p-[2px]">
                                <div className="w-full h-full rounded-full bg-obsidian-900 flex items-center justify-center text-3xl font-black text-white">
                                    {me?.email?.[0].toUpperCase()}
                                </div>
                            </div>
                            <h2 className="text-xl font-black text-white mb-1 truncate">{me?.full_name || 'Anonymous Operator'}</h2>
                            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-6">{me?.email}</p>
                            
                            <div className="flex items-center justify-center gap-4 py-4 border-t border-white/5">
                                <div>
                                    <div className="text-xl font-black text-brand-cyan">{me?.credits}</div>
                                    <div className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Credits</div>
                                </div>
                                <div className="w-px h-8 bg-white/5" />
                                <div>
                                    <div className="text-xl font-black text-white">PRO</div>
                                    <div className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Tier</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <Link href="/pricing" className="block">
                        <Button variant="glow" className="w-full h-14 font-black text-[10px] uppercase tracking-widest">
                            <CreditCard className="w-4 h-4 mr-2" /> Recharge Resource
                        </Button>
                    </Link>
                </div>

                {/* Right Column: Settings Groups */}
                <div className="md:col-span-2 space-y-8">
                    {/* Identity System */}
                    <div className="glass-panel rounded-[40px] border-white/5 overflow-hidden">
                        <div className="p-8 border-b border-white/5">
                            <h3 className="text-sm font-black text-white uppercase tracking-[0.2em] flex items-center gap-3">
                                <User className="w-4 h-4 text-brand-cyan" /> Identity Configuration
                            </h3>
                        </div>
                        <div className="p-4 space-y-1">
                            <div className="flex items-center justify-between p-4 rounded-[24px] hover:bg-white/[0.02] transition-colors group">
                                <div>
                                    <div className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Primary Email</div>
                                    <div className="text-sm font-bold text-white group-hover:text-brand-cyan transition-colors">{me?.email}</div>
                                </div>
                                <div className="px-3 py-1 rounded-lg bg-emerald-400/10 text-emerald-400 text-[10px] font-black uppercase tracking-widest border border-emerald-400/20">Verified</div>
                            </div>
                            <div className="flex items-center justify-between p-4 rounded-[24px] hover:bg-white/[0.02] transition-colors group cursor-not-allowed opacity-50">
                                <div>
                                    <div className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Security Key</div>
                                    <div className="text-sm font-bold text-white">••••••••••••</div>
                                </div>
                                <ChevronRight className="w-4 h-4 text-gray-700" />
                            </div>
                        </div>
                    </div>

                    {/* Administrative Protocol */}
                    <div className={`glass-panel rounded-[40px] border-white/5 overflow-hidden relative ${!me?.is_admin ? 'grayscale opacity-50' : ''}`}>
                        <div className="p-8 border-b border-white/5 flex items-center justify-between">
                            <h3 className="text-sm font-black text-white uppercase tracking-[0.2em] flex items-center gap-3">
                                <Shield className={`w-4 h-4 ${me?.is_admin ? 'text-brand-violet' : 'text-gray-500'}`} /> Administrative Access
                            </h3>
                            {me?.is_admin && (
                                <Sparkles className="w-4 h-4 text-brand-violet animate-pulse" />
                            )}
                        </div>
                        <div className="p-8 space-y-6">
                            <p className="text-sm font-bold text-gray-500 leading-relaxed uppercase tracking-tight">
                                {me?.is_admin 
                                    ? "Full node oversight enabled. Access real-time operation metrics, user management systems, and system health telemetries." 
                                    : "Administrative protocols are restricted to authorized entities. If you require elevated access, contact systems support."
                                }
                            </p>
                            
                            <Link href={me?.is_admin ? "/admin" : "#"}>
                                <Button 
                                    variant={me?.is_admin ? "primary" : "secondary"} 
                                    className="w-full h-14 font-black text-[10px] uppercase tracking-[0.2em]"
                                    disabled={!me?.is_admin}
                                >
                                    <Monitor className="w-4 h-4 mr-2" />
                                    {me?.is_admin ? 'Initialize Admin Console' : 'Access Restricted'}
                                </Button>
                            </Link>
                        </div>
                        
                        {!me?.is_admin && (
                            <div className="absolute inset-0 bg-obsidian-950/20 pointer-events-none" />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function AlertCircle({ className }: { className?: string }) {
    return (
        <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    )
}
