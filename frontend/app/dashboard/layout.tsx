'use client';
import { useState, useEffect } from 'react';
import Sidebar from '@/components/dashboard/Sidebar';
import TopBar from '@/components/dashboard/TopBar';
import BottomNav from '@/components/ui/BottomNav';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const [mounted, setMounted] = useState(false);
    useEffect(() => setMounted(true), []);

    return (
        <div className="min-h-screen bg-obsidian-950 text-white selection:bg-brand-cyan/30 overflow-x-hidden relative">
            {/* Ambient Background */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
                <div className="absolute top-[-10%] left-[-10%] w-[80vw] h-[80vw] bg-brand-cyan/5 rounded-full blur-[120px] animate-pulse-slow" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[80vw] h-[80vw] bg-brand-violet/5 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
                <div className="absolute inset-0 bg-grid-pattern opacity-10" />
            </div>

            {mounted ? <Sidebar /> : <div className="fixed left-4 top-4 bottom-4 w-64 glass-panel rounded-2xl hidden md:block opacity-20" />}

            {/* Main Content Area - Dynamic Padding */}
            <div className={`relative z-10 min-h-screen flex flex-col transition-all duration-500 ${mounted ? 'pl-0 md:pl-72 pb-24 md:pb-0' : 'pl-0 md:pl-72'}`}>
                <TopBar />
                <main className="flex-1 px-4 md:px-8 py-6">
                    {children}
                </main>
            </div>

            {mounted && <BottomNav />}
        </div>
    );
}
