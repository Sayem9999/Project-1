'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { API_BASE } from '@/lib/api';

export default function TopBar() {
    const pathname = usePathname();
    const router = useRouter();
    const [credits, setCredits] = useState<number | null>(null);

    // Format pathname for breadcrumbs (e.g. /dashboard/upload -> Dashboard / Upload)
    const segments = pathname.split('/').filter(Boolean);

    useEffect(() => {
        const fetchCredits = async () => {
            const token = localStorage.getItem('token');
            if (!token) return;

            try {
                const res = await fetch(`${API_BASE}/auth/me`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setCredits(data.credits);
                }
            } catch (err) {
                console.error("Failed to fetch credits", err);
            }
        };

        fetchCredits();

        // Listen for credit updates (simple event bus for now)
        const handleCreditUpdate = () => fetchCredits();
        window.addEventListener('credit-update', handleCreditUpdate);
        return () => window.removeEventListener('credit-update', handleCreditUpdate);
    }, []);

    return (
        <header className="h-16 flex items-center justify-between px-8 bg-[#0a0a0f]/80 backdrop-blur-md sticky top-0 z-40 border-b border-white/5 ml-64">
            {/* Breadcrumbs */}
            <div className="flex items-center gap-2 text-sm">
                {segments.map((segment, i) => (
                    <div key={segment} className="flex items-center gap-2">
                        {i > 0 && <span className="text-gray-600">/</span>}
                        <span className={`capitalize ${i === segments.length - 1 ? 'text-white font-medium' : 'text-gray-500'}`}>
                            {segment}
                        </span>
                    </div>
                ))}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
                {/* Credits Badge */}
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700/50 text-xs font-semibold text-slate-300">
                    <span className="text-amber-400">🪙</span>
                    <span>{credits !== null ? credits : '...'} Credits</span>
                    <button onClick={() => router.push('/pricing')} className="ml-2 w-5 h-5 rounded-full bg-cyan-500 text-black flex items-center justify-center hover:bg-cyan-400" title="Buy Credits">
                        +
                    </button>
                </div>

                <div className="w-px h-6 bg-white/10 mx-2" />

                <button className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-gray-400 transition-colors">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </button>
                <button className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-gray-400 transition-colors relative">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                    <span className="absolute top-2 right-2 w-2 h-2 bg-cyan-500 rounded-full border-2 border-[#0a0a0f]" />
                </button>

                <Link
                    href="/dashboard/upload"
                    className="flex items-center gap-2 px-4 py-2 bg-white text-black rounded-full text-sm font-semibold hover:bg-gray-100 transition-colors"
                >
                    <span>+</span>
                    <span>New Project</span>
                </Link>
            </div>
        </header>
    );
}
