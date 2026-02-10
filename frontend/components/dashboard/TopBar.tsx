'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

// Ensure this matches the backend port
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

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
        <header className="h-20 flex items-center justify-between px-8 z-40">
            {/* Breadcrumbs */}
            <div className="flex items-center gap-2 text-sm">
                {segments.map((segment, i) => (
                    <div key={segment} className="flex items-center gap-2">
                        {i > 0 && <span className="text-gray-600">/</span>}
                        <span className={`capitalize font-display tracking-wide ${i === segments.length - 1 ? 'text-white font-medium' : 'text-gray-500'}`}>
                            {segment}
                        </span>
                    </div>
                ))}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-6">
                {/* Credits Badge */}
                <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-xl bg-obsidian-800/50 border border-white/5 text-xs font-semibold text-slate-300 shadow-sm backdrop-blur-sm">
                    <span className="text-amber-400 text-base">CR</span>
                    <span className="font-mono tracking-wider">{credits !== null ? credits : '...'} CR</span>
                    <div className="w-px h-3 bg-white/10 mx-2" />
                    <button className="text-brand-cyan hover:text-white transition-colors" title="Buy Credits">
                        GET MORE
                    </button>
                </div>

                <div className="flex items-center gap-3">
                    <button className="w-10 h-10 rounded-xl glass-card flex items-center justify-center text-gray-400 hover:text-white transition-colors">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </button>
                    <button className="w-10 h-10 rounded-xl glass-card flex items-center justify-center text-gray-400 hover:text-white transition-colors relative">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                        <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-brand-cyan rounded-full shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
                    </button>

                    <div className="w-px h-6 bg-white/10 mx-2" />

                    <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-cyan to-brand-violet p-[1px]">
                        <div className="w-full h-full rounded-xl bg-obsidian-900 overflow-hidden">
                            <Image
                                src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
                                alt="User"
                                width={40}
                                height={40}
                                className="w-full h-full object-cover"
                                unoptimized
                            />
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
