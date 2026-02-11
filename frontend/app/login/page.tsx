'use client';
import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { apiRequest, ApiError, setAuthToken, setStoredUser } from '@/lib/api';
import { useToast } from '@/components/ui/Toast';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState(false);
  const { showToast } = useToast();
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [adminMode, setAdminMode] = useState(false);

  useEffect(() => {
    const emailParam = searchParams.get('email');
    const messageParam = searchParams.get('message');
    const adminParam = searchParams.get('admin');
    if (emailParam) setEmail(emailParam);
    setAdminMode(adminParam === '1' || adminParam === 'true');
    if (messageParam === 'exists') {
      setInfo('Account already exists. Please sign in.');
    }
  }, [searchParams]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = adminMode ? '/auth/admin/login' : '/auth/login';
      const data = await apiRequest<{ access_token: string }>(endpoint, {
        method: 'POST',
        body: { email, password },
      });

      setAuthToken(data.access_token);
      try {
        const me = await apiRequest<any>('/auth/me', { auth: true });
        setStoredUser(me);
        if (adminMode && !me.is_admin) {
          setError('Admin access required');
          setLoading(false);
          return;
        }
        if (me.is_admin) {
          showToast("Welcome, Administrator", "success");
        }
      } catch {
        // no-op for now
      }
      router.push(adminMode ? '/admin' : '/dashboard/upload');
    } catch (err: any) {
      const message = err instanceof ApiError ? err.message : 'Login failed';
      setError(message);
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setOauthLoading(true);
    try {
      const data = await apiRequest<{ auth_url?: string }>('/auth/oauth/google');
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    } catch {
      setError('Google login unavailable');
      setOauthLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <Link href="/" className="flex items-center justify-center gap-3 mb-10">
        <Image src="/logo.svg" alt="Proedit" width={48} height={48} className="w-12 h-12" priority />
        <span className="text-2xl font-bold">
          <span className="text-white">Pro</span>
          <span className="text-cyan-400">edit</span>
        </span>
      </Link>

      <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
        <h1 className="text-2xl font-bold text-white text-center mb-2">
          {adminMode ? 'Admin sign in' : 'Sign in'}
        </h1>
        <p className="text-gray-400 text-center mb-6">
          {adminMode ? 'Sign in with an admin account' : 'Sign in to your account'}
        </p>

        {info && (
          <div className="p-3 mb-4 bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-cyan-400 text-sm text-center">
            {info}
          </div>
        )}

        <button
          onClick={handleGoogleLogin}
          disabled={oauthLoading}
          className="w-full flex items-center justify-center gap-3 py-3.5 px-4 bg-white rounded-xl text-gray-900 font-medium hover:bg-gray-100 transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          {oauthLoading ? (
            <span className="animate-spin text-xl">...</span>
          ) : (
            <>
              <Image
                src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                alt=""
                width={20}
                height={20}
                className="w-5 h-5"
                unoptimized
              />
              Continue with Google
            </>
          )}
        </button>

        <div className="flex items-center gap-4 my-6">
          <div className="flex-1 h-px bg-white/10" />
          <span className="text-xs text-gray-500 uppercase">or</span>
          <div className="flex-1 h-px bg-white/10" />
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3.5 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
            placeholder="Email address"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3.5 bg-slate-800/50 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
            placeholder="Password"
            required
          />

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm text-center">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-xl text-white font-semibold hover:opacity-90 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <button
          onClick={() => router.push('/')}
          className="w-full mt-4 py-3 text-gray-400 hover:text-white transition-colors text-sm"
        >
          Cancel
        </button>

        <p className="text-center text-sm text-gray-400 mt-4">
          Don&apos;t have an account{' '}
          <Link href="/signup" className="text-cyan-400 hover:underline">Sign up</Link>
        </p>
        <p className="text-center text-sm text-gray-500 mt-2">
          {adminMode ? (
            <Link href="/login" className="text-cyan-400 hover:underline">Back to user login</Link>
          ) : (
            <Link href="/login?admin=1" className="text-cyan-400 hover:underline">Admin login</Link>
          )}
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <main className="min-h-screen relative overflow-hidden">
      <div className="fixed inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/20 rounded-full blur-[128px] animate-pulse" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-violet-500/20 rounded-full blur-[128px] animate-pulse" style={{ animationDelay: '1s' }} />
        </div>
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />
      </div>

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-6">
        <div className="absolute top-6 left-6">
          <Link
            href="/"
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition-all"
          >
            <span>Back</span>
          </Link>
        </div>

        <Suspense fallback={<div className="text-white">Loading...</div>}>
          <LoginForm />
        </Suspense>
      </div>
    </main>
  );
}
