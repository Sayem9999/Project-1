'use client';
import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiRequest, ApiError, setAuthToken, setStoredUser } from '@/lib/api';

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
        <div className="bg-[#12121a] border border-white/10 p-8 rounded-2xl text-center space-y-4 max-w-md w-full">
            {error ? (
                <>
                    <div className="w-16 h-16 mx-auto bg-red-500/20 rounded-full flex items-center justify-center text-3xl">
                        X
                    </div>
                    <h2 className="text-xl font-bold text-white">Authentication Failed</h2>
                    <p className="text-gray-400">{error}</p>
                    <button
                        onClick={() => router.push('/login')}
                        className="w-full py-3 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-xl text-white font-semibold hover:opacity-90 transition-opacity"
                    >
                        Back to Login
                    </button>
                </>
            ) : (
                <>
                    <div className="w-16 h-16 mx-auto relative">
                        <div className="absolute inset-0 rounded-full border-t-2 border-cyan-500 animate-spin"></div>
                    </div>
                    <h2 className="text-xl font-bold text-white">Signing you in...</h2>
                    <p className="text-gray-400">Connecting with Google</p>
                </>
            )}
        </div>
    );
}

export default function GoogleCallbackPage() {
    return (
        <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-6">
            <Suspense fallback={
                <div className="bg-[#12121a] border border-white/10 p-8 rounded-2xl text-center space-y-4 max-w-md w-full">
                    <div className="w-16 h-16 mx-auto relative">
                        <div className="absolute inset-0 rounded-full border-t-2 border-cyan-500 animate-spin"></div>
                    </div>
                    <h2 className="text-xl font-bold text-white">Loading...</h2>
                </div>
            }>
                <GoogleCallbackContent />
            </Suspense>
        </div>
    );
}
