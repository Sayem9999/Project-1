'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/ui/Navbar';

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
    <main className="min-h-screen bg-[#0a0a0f] flex flex-col">
      <Navbar />

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="bg-[#12121a] border border-white/10 rounded-2xl p-8">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center">
                <span className="text-2xl">🎬</span>
              </div>
              <h1 className="text-2xl font-bold text-white">Create your account</h1>
              <p className="text-gray-400 text-sm mt-1">Start editing videos with AI today</p>
            </div>

            {/* Free Badge */}
            <div className="flex items-center justify-center gap-2 mb-6 py-2 px-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
              <span className="text-emerald-400">✓</span>
              <span className="text-sm text-emerald-400">5 free renders included</span>
            </div>

            {/* Google Button */}
            <button
              onClick={handleGoogleSignup}
              disabled={oauthLoading}
              className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-white rounded-xl text-gray-900 font-medium hover:bg-gray-100 transition-colors mb-6"
            >
              {oauthLoading ? (
                <span className="animate-spin">⟳</span>
              ) : (
                <>
                  <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" className="w-5 h-5" />
                  Sign up with Google
                </>
              )}
            </button>

            {/* Divider */}
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1 h-px bg-white/10" />
              <span className="text-xs text-gray-500 uppercase">or</span>
              <div className="flex-1 h-px bg-white/10" />
            </div>

            {/* Form */}
            <form onSubmit={handleSignup} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-[#1a1a26] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors"
                  placeholder="you@example.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-[#1a1a26] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors"
                  placeholder="Min 6 characters"
                  required
                  minLength={6}
                />
              </div>

              {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-xl text-white font-semibold hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {loading ? 'Creating account...' : 'Create Account'}
              </button>
            </form>

            {/* Terms */}
            <p className="text-xs text-gray-500 text-center mt-4">
              By signing up, you agree to our{' '}
              <Link href="/terms" className="text-cyan-400 hover:underline">Terms</Link>
              {' '}and{' '}
              <Link href="/privacy" className="text-cyan-400 hover:underline">Privacy Policy</Link>
            </p>

            {/* Footer */}
            <p className="text-center text-sm text-gray-400 mt-6">
              Already have an account?{' '}
              <Link href="/login" className="text-cyan-400 hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
