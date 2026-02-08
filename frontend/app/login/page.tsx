'use client';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch } from '@/lib/api';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
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

  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <div className="glass-panel w-full max-w-md p-8 rounded-2xl relative overflow-hidden">
        {/* Decorative Glows */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-brand-cyan/10 blur-3xl rounded-full pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-brand-violet/10 blur-3xl rounded-full pointer-events-none"></div>

        <h1 className="text-3xl font-bold mb-6 text-center text-white text-glow">Welcome Back</h1>

        <form onSubmit={submit} className="space-y-6 relative z-10">
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
            Login to Studio
          </button>

          {error && (
            <div className="p-3 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
              {error}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
