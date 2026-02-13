'use client';
import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiRequest, ApiError, setAuthToken, setStoredUser } from '@/lib/api';
import { Activity, Shield, AlertTriangle, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

function GoogleCallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [error, setError] = useState('');

    useEffect(() => {
        const code = searchParams.get('code');

        if (!code) {
            setError('No authorization code received');
            return;
        }

        apiRequest<{ access_token: string; user?: unknown }>(
            `/auth/oauth/google/callback?code=${encodeURIComponent(code)}`,
            { method: 'POST' }
        )
            .then(data => {
                setAuthToken(data.access_token);
                if (data.user) setStoredUser(data.user);
                router.push('/dashboard/upload');
            })
            .catch(err => {
                console.error('OAuth error:', err);
                setError(err instanceof ApiError ? err.message : 'Authentication failed. Please try again.');
            });
    }, [searchParams, router]);

    return (
        <div className="w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-1000 relative z-10">
            <div className="glass-panel p-10 rounded-[48px] border-white/5 relative overflow-hidden text-center">
                <div className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-brand-cyan/10 to-transparent" />

                {error ? (
                    <div className="relative z-10 space-y-8">
                        <div className="w-20 h-20 mx-auto bg-red-500/10 rounded-[32px] flex items-center justify-center border border-red-500/20">
                            <AlertTriangle className="w-10 h-10 text-red-500" />
                        </div>
                        <div className="space-y-2">
                            <h2 className="text-2xl font-black text-white uppercase tracking-tight">Access Denied</h2>
                            <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest leading-loose">The Identity Provider returned an error during sync.</p>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/5 border border-white/5 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-center">
                            {error}
                        </div>
                        <Link href="/login" className="block">
                            <button className="w-full h-14 bg-white text-black rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-gray-200 transition-colors">
                                Return to Terminal
                            </button>
                        </Link>
                    </div>
                ) : (
                    <div className="relative z-10 space-y-8 py-10">
                        <div className="relative w-20 h-20 mx-auto">
                            <div className="absolute inset-0 rounded-[32px] border-4 border-brand-cyan/20"></div>
                            <div className="absolute inset-0 rounded-[32px] border-t-4 border-brand-cyan animate-spin"></div>
                            <Activity className="absolute inset-0 m-auto w-8 h-8 text-brand-cyan animate-pulse" />
                        </div>
                        <div className="space-y-2">
                            <h2 className="text-2xl font-black text-white uppercase tracking-tight">Syncing Node</h2>
                            <p className="text-[10px] font-black text-brand-cyan uppercase tracking-[0.3em] animate-pulse">Establishing Session Protocol</p>
                        </div>
                        <div className="flex items-center justify-center gap-3">
                            <Shield className="w-4 h-4 text-emerald-400" />
                            <span className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Secure Identity Verification</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default function GoogleCallbackPage() {
    return (
        <main className="min-h-screen relative overflow-hidden bg-obsidian-950 flex flex-col items-center justify-center p-6">
            {/* Ambient Background */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-[-10%] right-[-10%] w-[80vw] h-[80vw] bg-brand-cyan/5 rounded-full blur-[120px] animate-pulse-slow" />
                <div className="absolute bottom-[-10%] left-[-10%] w-[80vw] h-[80vw] bg-brand-violet/5 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
                <div className="absolute inset-0 bg-grid-pattern opacity-10" />
            </div>

            <Suspense fallback={
                <div className="w-full max-w-md glass-panel p-10 rounded-[48px] border-white/5 relative z-10 bg-obsidian-900/50 flex flex-col items-center justify-center py-20 gap-8">
                    <div className="w-12 h-12 border-4 border-brand-cyan/20 border-t-brand-cyan rounded-full animate-spin" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-gray-500">Initializing Node</span>
                </div>
            }>
                <GoogleCallbackContent />
            </Suspense>
        </main>
    );
}
