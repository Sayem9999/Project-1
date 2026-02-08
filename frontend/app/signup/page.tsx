'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_BASE}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Signup failed');

      localStorage.setItem('token', data.access_token);
      router.push('/dashboard/upload');
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    setOauthLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/oauth/google`);
      const data = await res.json();
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    } catch {
      setError('Google signup unavailable');
      setOauthLoading(false);
    }
  };

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-20 right-10 w-72 h-72 bg-violet-500/20 rounded-full blur-[128px] animate-pulse" />
          <div className="absolute bottom-20 left-10 w-96 h-96 bg-cyan-500/20 rounded-full blur-[128px] animate-pulse" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-emerald-500/10 rounded-full blur-[100px]" />
        </div>
        {/* Grid overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />
      </div>

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-6">
        {/* Back Button */}
        <div className="absolute top-6 left-6">
          <Link
            href="/"
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition-all"
          >
            <span>←</span>
            <span>Back</span>
          </Link>
        </div>

        <div className="w-full max-w-md">
          {/* Logo */}
          <Link href="/" className="flex items-center justify-center gap-3 mb-10">
            <img src="/logo.svg" alt="Proedit" className="w-12 h-12" />
            <span className="text-2xl font-bold">
              <span className="text-white">Pro</span>
              <span className="text-cyan-400">edit</span>
            </span>
          </Link>

          {/* Card */}
          <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
            <h1 className="text-2xl font-bold text-white text-center mb-2">Create an account</h1>
            <p className="text-gray-400 text-center mb-6">Start editing videos with AI</p>

            {/* Free Badge */}
            <div className="flex items-center justify-center gap-2 mb-6 py-2.5 px-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
              <span className="text-emerald-400">✓</span>
              <span className="text-sm text-emerald-400">5 free renders included</span>
            </div>

            {/* Google */}
            <button
              onClick={handleGoogleSignup}
              disabled={oauthLoading}
              className="w-full flex items-center justify-center gap-3 py-3.5 px-4 bg-white rounded-xl text-gray-900 font-medium hover:bg-gray-100 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              {oauthLoading ? (
                <span className="animate-spin text-xl">⟳</span>
              ) : (
                <>
                  <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="" className="w-5 h-5" />
                  Sign up with Google
                </>
              )}
            </button>

            <div className="flex items-center gap-4 my-6">
              <div className="flex-1 h-px bg-white/10" />
              <span className="text-xs text-gray-500 uppercase">or</span>
              <div className="flex-1 h-px bg-white/10" />
            </div>

            <form onSubmit={handleSignup} className="space-y-4">
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
                placeholder="Password (min 6 characters)"
                required
                minLength={6}
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
                {loading ? 'Creating account...' : 'Create account'}
              </button>
            </form>

            {/* Cancel */}
            <button
              onClick={() => router.push('/')}
              className="w-full mt-4 py-3 text-gray-400 hover:text-white transition-colors text-sm"
            >
              Cancel
            </button>

            <p className="text-xs text-gray-500 text-center mt-4">
              By signing up, you agree to our <Link href="/terms" className="underline hover:text-gray-400">Terms</Link> and <Link href="/privacy" className="underline hover:text-gray-400">Privacy</Link>
            </p>

            <p className="text-center text-sm text-gray-400 mt-4">
              Already have an account?{' '}
              <Link href="/login" className="text-cyan-400 hover:underline">Sign in</Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
