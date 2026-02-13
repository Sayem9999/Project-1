'use client';
import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { apiRequest, ApiError, setAuthToken, setStoredUser } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Sparkles, Shield, ArrowLeft } from 'lucide-react';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState(false);
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
      const me = await apiRequest<any>('/auth/me', { auth: true });
      setStoredUser(me);

      if (adminMode && !me.is_admin) {
        setError('Admin access required');
        setLoading(false);
        return;
      }

      router.push(adminMode ? '/admin' : '/dashboard/upload');
    } catch (err: any) {
      setError(err instanceof ApiError ? err.message : 'Login failed');
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setOauthLoading(true);
    try {
      const data = await apiRequest<{ auth_url?: string }>('/auth/oauth/google');
      if (data.auth_url) window.location.href = data.auth_url;
    } catch {
      setError('Google login unavailable');
      setOauthLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-1000">
      <div className="text-center mb-10">
        <Link href="/" className="inline-flex items-center gap-3 mb-6 group">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-cyan to-brand-violet p-[2px] group-hover:rotate-6 transition-transform">
            <div className="w-full h-full rounded-[14px] bg-obsidian-900 flex items-center justify-center font-black text-xl text-white">P</div>
          </div>
          <span className="text-3xl font-black tracking-tighter uppercase">PROEDIT</span>
        </Link>
        <h1 className="text-2xl font-black text-white tracking-tight">{adminMode ? 'Elevated Access' : 'Welcome Back'}</h1>
        <p className="text-gray-500 text-sm mt-1 uppercase tracking-[0.2em] font-bold">Secure Authentication Protocol</p>
      </div>

      <div className="glass-panel p-8 md:p-10 rounded-[40px] border-white/5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-brand-cyan/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

        {info && (
          <div className="mb-6 p-4 rounded-2xl bg-brand-cyan/10 border border-brand-cyan/20 text-brand-cyan text-[10px] font-black uppercase tracking-widest text-center">
            {info}
          </div>
        )}

        <Button
          onClick={handleGoogleLogin}
          loading={oauthLoading}
          variant="secondary"
          className="w-full mb-8 font-black text-xs uppercase tracking-widest bg-white text-black hover:bg-gray-100 border-none h-14"
        >
          <Image
            src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
            alt="" width={18} height={18} className="mr-3" unoptimized
          />
          Continue with Google
        </Button>

        <div className="flex items-center gap-4 mb-8">
          <div className="flex-1 h-px bg-white/5" />
          <span className="text-[10px] font-black text-gray-600 uppercase tracking-widest">OR IDENTITY_SYNC</span>
          <div className="flex-1 h-px bg-white/5" />
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Email Terminal</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl text-white placeholder-gray-600 focus:outline-none focus:border-brand-cyan/50 transition-all font-bold text-sm"
              placeholder="OPERATOR_EMAIL"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Password Key</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl text-white placeholder-gray-600 focus:outline-none focus:border-brand-cyan/50 transition-all font-bold text-sm"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-500 text-[10px] font-black uppercase tracking-widest text-center animate-in shake-1">
              {error}
            </div>
          )}

          <Button
            type="submit"
            loading={loading}
            variant="glow"
            className="w-full h-14 font-black text-xs uppercase tracking-[0.2em] mt-4"
          >
            Initialize Session
          </Button>
        </form>

        <div className="mt-10 pt-8 border-t border-white/5 space-y-4 text-center">
          <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">
            New Operator? <Link href="/signup" className="text-brand-cyan hover:text-brand-accent ml-1 transition-colors">Register Access</Link>
          </p>
          {adminMode ? (
            <Link href="/login" className="block text-[10px] font-black text-brand-violet uppercase tracking-widest hover:opacity-80 transition-opacity">Return to Standard Node</Link>
          ) : (
            <Link href="/login?admin=1" className="block text-[10px] font-bold text-gray-700 uppercase tracking-widest hover:text-brand-cyan transition-colors">Administrative Override</Link>
          )}
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <main className="min-h-screen relative overflow-hidden bg-obsidian-950 flex flex-col items-center justify-center p-6">
      {/* Ambient Experience Layer */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[80vw] h-[80vw] bg-brand-cyan/5 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[80vw] h-[80vw] bg-brand-violet/5 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute inset-0 bg-grid-pattern opacity-10" />
      </div>

      <Link href="/" className="absolute top-8 left-8 flex items-center gap-3 text-gray-500 hover:text-white transition-all group z-20">
        <div className="p-2.5 rounded-xl bg-white/5 border border-white/5 group-hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </div>
        <span className="text-[10px] font-black uppercase tracking-[0.3em] hidden sm:block">Back to Lab</span>
      </Link>

      <div className="relative z-10 w-full flex justify-center">
        <Suspense fallback={
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 border-4 border-brand-cyan/20 border-t-brand-cyan rounded-full animate-spin mb-4" />
            <span className="text-[10px] font-black uppercase tracking-widest text-gray-500">Syncing Node</span>
          </div>
        }>
          <LoginForm />
        </Suspense>
      </div>
    </main>
  );
}
