'use client';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import { apiRequest, ApiError, API_ORIGIN, clearAuth, setStoredUser } from '@/lib/api';
import { Search, Bell, Clock, Activity } from 'lucide-react';

export default function TopBar() {
    const pathname = usePathname();
    const [credits, setCredits] = useState<number | null>(null);
    const [displayName, setDisplayName] = useState<string>('U');
    const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
    const [clock, setClock] = useState<string>('');
    const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);
    const [localOnly, setLocalOnly] = useState<boolean>(false);

    useEffect(() => {
        const stored = localStorage.getItem('local_only_mode');
        if (stored === 'true') setLocalOnly(true);
    }, []);

    const segments = pathname.split('/').filter(Boolean);

    useEffect(() => {
        const fetchCredits = async () => {
            try {
                const data = await apiRequest<{ credits?: number; full_name?: string; email?: string; avatar_url?: string }>(
                    '/auth/me',
                    { auth: true }
                );
                setCredits(data.credits ?? 0);
                setDisplayName(data.full_name || data.email || 'U');
                setAvatarUrl(data.avatar_url || null);
                setStoredUser(data);
            } catch (err) {
                if (err instanceof ApiError && err.isAuth) {
                    clearAuth();
                    return;
                }
            }
        };

        fetchCredits();
        const handleCreditUpdate = () => fetchCredits();
        window.addEventListener('credit-update', handleCreditUpdate);
        return () => window.removeEventListener('credit-update', handleCreditUpdate);
    }, []);

    useEffect(() => {
        const updateClock = () => setClock(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        updateClock();
        const timer = window.setInterval(updateClock, 1000);
        return () => window.clearInterval(timer);
    }, []);

    useEffect(() => {
        let cancelled = false;
        const checkHealth = async () => {
            try {
                const res = await fetch(`${API_ORIGIN}/health`, { method: 'GET' });
                if (!cancelled) setApiHealthy(res.ok);
            } catch {
                if (!cancelled) setApiHealthy(false);
            }
        };
        checkHealth();
        const interval = window.setInterval(checkHealth, 30000);
        return () => { cancelled = true; window.clearInterval(interval); };
    }, []);

    return (
        <header className="h-20 flex items-center justify-between px-4 md:px-8 z-40 relative">
            {/* Breadcrumbs - Hidden on Mobile */}
            <div className="hidden md:flex items-center gap-2 text-sm">
                {segments.map((segment, i) => (
                    <div key={segment} className="flex items-center gap-2">
                        {i > 0 && <span className="text-gray-600">/</span>}
                        <span className={`capitalize font-display tracking-tight ${i === segments.length - 1 ? 'text-white font-bold' : 'text-gray-500'}`}>
                            {segment}
                        </span>
                    </div>
                ))}
            </div>

            {/* Mobile Brand Placeholder (since sidebar is hidden) */}
            <div className="md:hidden flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-cyan to-brand-violet flex items-center justify-center text-white font-bold text-xs ring-2 ring-white/10">
                    P
                </div>
                <span className="text-sm font-bold tracking-tight text-white uppercase">Proedit</span>
            </div>

            {/* Actions Area */}
            <div className="flex items-center gap-3 md:gap-6">
                {/* System Status - Hidden on extra small phones */}
                <div className="hidden sm:flex items-center gap-3 px-3 py-1.5 rounded-full glass-sm text-[10px] h-9">
                    <div className="flex items-center gap-1.5 border-r border-white/5 pr-3">
                        <div className={`w-1.5 h-1.5 rounded-full ${apiHealthy ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]' : 'bg-red-400'}`} />
                        <span className="text-gray-400 uppercase tracking-widest font-bold">API</span>
                    </div>
                    <span className="font-mono text-gray-300">{clock}</span>
                </div>

                {/* Local Mode Toggle */}
                <div className="flex items-center gap-3 px-3 py-1.5 rounded-full glass-md border-white/5 h-9">
                    <span className="text-[9px] font-black text-gray-500 uppercase tracking-tighter">Local Only</span>
                    <button
                        onClick={() => {
                            const newState = !localOnly;
                            setLocalOnly(newState);
                            localStorage.setItem('local_only_mode', String(newState));
                        }}
                        className={`w-8 h-4 rounded-full relative transition-colors duration-300 ${localOnly ? 'bg-brand-cyan' : 'bg-white/10'}`}
                    >
                        <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all duration-300 shadow-sm ${localOnly ? 'left-4' : 'left-0.5'}`} />
                    </button>
                </div>

                {/* Credits - Visible on most screens */}
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full glass-md border-brand-cyan/20 text-[10px] font-bold text-slate-300 h-9">
                    <span className="text-brand-cyan">CR</span>
                    <span className="font-mono">{credits !== null ? credits : '...'}</span>
                    <button className="ml-1 text-white/50 hover:text-brand-cyan transition-colors" title="Add Credits">+</button>
                </div>

                {/* Icon Actions */}
                <div className="flex items-center gap-1 md:gap-2">
                    <button className="w-9 h-9 rounded-full hover:bg-white/5 flex items-center justify-center text-gray-400 hidden lg:flex">
                        <Search className="w-4 h-4" />
                    </button>
                    <button className="w-9 h-9 rounded-full hover:bg-white/5 flex items-center justify-center text-gray-400 relative">
                        <Bell className="w-4 h-4" />
                        <span className="absolute top-2 right-2 w-2 h-2 bg-brand-cyan rounded-full shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
                    </button>

                    <div className="w-0.5 h-4 bg-white/5 mx-1 hidden sm:block" />

                    {/* Profile */}
                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-brand-cyan to-brand-violet p-[1.5px] cursor-pointer hover:rotate-6 transition-transform">
                        <div className="w-full h-full rounded-full bg-obsidian-900 overflow-hidden flex items-center justify-center">
                            {avatarUrl ? (
                                <Image src={avatarUrl} alt="U" width={36} height={36} className="w-full h-full object-cover" unoptimized />
                            ) : (
                                <span className="text-xs font-bold text-white uppercase">{displayName.charAt(0)}</span>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
