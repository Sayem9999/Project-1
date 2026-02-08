'use client';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export default function GitHubCallbackPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [error, setError] = useState('');

    useEffect(() => {
        const code = searchParams.get('code');

        if (!code) {
            setError('No authorization code received');
            return;
        }

        // Exchange code for token
        fetch(`${API_BASE}/auth/oauth/github/callback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
        })
            .then(res => {
                if (!res.ok) throw new Error('Authentication failed');
                return res.json();
            })
            .then(data => {
                // Store token and user info
                localStorage.setItem('token', data.access_token);
                if (data.user) {
                    localStorage.setItem('user', JSON.stringify(data.user));
                }
                // Redirect to dashboard
                router.push('/dashboard/upload');
            })
            .catch(err => {
                console.error('OAuth error:', err);
                setError('Authentication failed. Please try again.');
            });
    }, [searchParams, router]);

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="glass-panel p-8 rounded-xl text-center space-y-4 max-w-md">
                {error ? (
                    <>
                        <div className="w-16 h-16 mx-auto bg-red-500/20 rounded-full flex items-center justify-center">
                            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-bold text-white">Authentication Failed</h2>
                        <p className="text-slate-400">{error}</p>
                        <button onClick={() => router.push('/login')} className="btn-primary w-full">
                            Back to Login
                        </button>
                    </>
                ) : (
                    <>
                        <div className="w-16 h-16 mx-auto relative">
                            <div className="absolute inset-0 rounded-full border-t-2 border-brand-violet animate-spin"></div>
                        </div>
                        <h2 className="text-xl font-bold text-white">Signing you in...</h2>
                        <p className="text-slate-400">Connecting with GitHub</p>
                    </>
                )}
            </div>
        </div>
    );
}
