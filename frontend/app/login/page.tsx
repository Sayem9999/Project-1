'use client';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch } from '@/lib/api';
import Link from 'next/link';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [googleLoading, setGoogleLoading] = useState(false);
  const router = useRouter();

  async function submit(e: FormEvent) {
    e.preventDefault();
    try {
      const res = await apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
      if (!res.ok) {
        const errText = await res.text();
        return setError(`Login failed: ${errText.replace(/"/g, '')}`);
      }
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      router.push('/dashboard/upload');
    } catch (e) {
      setError(`Network error: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  async function handleGoogleLogin() {
    setGoogleLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/oauth/google`);
      if (!res.ok) throw new Error('Google OAuth not configured');
      const data = await res.json();
      window.location.href = data.auth_url;
    } catch {
      setError('Google login is not available.');
      setGoogleLoading(false);
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="glass-panel w-full max-w-md p-8 rounded-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-brand-cyan/10 blur-3xl rounded-full pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-brand-violet/10 blur-3xl rounded-full pointer-events-none"></div>

        <h1 className="text-3xl font-bold mb-2 text-center text-white text-glow">Welcome Back</h1>
        <p className="text-slate-400 text-center mb-6">Sign in to your studio</p>

        {/* Google OAuth */}
        <button
          onClick={handleGoogleLogin}
          disabled={googleLoading}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg bg-white text-gray-800 font-medium hover:bg-gray-100 transition-all disabled:opacity-50 mb-6"
        >
          {googleLoading ? (
            <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
          )}
          Continue with Google
        </button>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-700"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 bg-slate-900 text-slate-500">or</span>
          </div>
        </div>

        <form onSubmit={submit} className="space-y-5 relative z-10">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Email</label>
            <input
              className="glass-input w-full"
              placeholder="editor@example.com"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Password</label>
            <input
              type="password"
              className="glass-input w-full"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button className="btn-primary w-full py-4 text-lg shadow-lg">
            Login
          </button>

          {error && (
            <div className="p-3 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
              {error}
            </div>
          )}
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Don't have an account?{' '}
          <Link href="/signup" className="text-brand-cyan hover:underline">Sign up free</Link>
        </p>
      </div>
    </div>
  );
}
