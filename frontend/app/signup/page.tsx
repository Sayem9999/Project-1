'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { apiRequest, ApiError, setAuthToken, setStoredUser } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { ArrowLeft, Sparkles, CheckCircle2 } from 'lucide-react';

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
      const data = await apiRequest<{ access_token: string }>('/auth/signup', {
        method: 'POST',
        body: { email, password },
      });

      setAuthToken(data.access_token);
      const me = await apiRequest('/auth/me', { auth: true });
      setStoredUser(me);
      router.push('/dashboard/upload');
    } catch (err: any) {
      if (err instanceof ApiError && err.code === 'email_already_exists') {
        router.push(`/login?email=${encodeURIComponent(email)}&message=exists`);
        return;
      }
      setError(err instanceof ApiError ? err.message : 'Signup failed');
      setLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    setOauthLoading(true);
    try {
      const data = await apiRequest<{ auth_url?: string }>('/auth/oauth/google');
      if (data.auth_url) window.location.href = data.auth_url;
    } catch {
      setError('Google signup unavailable');
      setOauthLoading(false);
    }
  };

  return (
    <main className="min-h-screen relative overflow-hidden bg-obsidian-950 flex flex-col items-center justify-center p-6">
      {/* Ambient Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] w-[80vw] h-[80vw] bg-brand-cyan/5 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[80vw] h-[80vw] bg-brand-violet/5 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute inset-0 bg-grid-pattern opacity-10" />
      </div>

      <Link href="/" className="absolute top-8 left-8 flex items-center gap-3 text-gray-500 hover:text-white transition-all group z-20">
        <div className="p-2.5 rounded-xl bg-white/5 border border-white/5 group-hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </div>
        <span className="text-[10px] font-black uppercase tracking-[0.3em] hidden sm:block">Back to Lab</span>
      </Link>

      <div className="w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-1000 relative z-10">
        <div className="text-center mb-10">
          <Link href="/" className="inline-flex items-center gap-3 mb-6 group">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-cyan to-brand-violet p-[2px] group-hover:rotate-6 transition-transform">
              <div className="w-full h-full rounded-[14px] bg-obsidian-900 flex items-center justify-center font-black text-xl text-white">P</div>
            </div>
            <span className="text-3xl font-black tracking-tighter uppercase">PROEDIT</span>
          </Link>
          <h1 className="text-2xl font-black text-white tracking-tight">Create Identity</h1>
          <p className="text-gray-500 text-sm mt-1 uppercase tracking-[0.2em] font-bold">New Operator Registration</p>
        </div>

        <div className="glass-panel p-8 md:p-10 rounded-[40px] border-white/5 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-32 h-32 bg-brand-violet/10 rounded-full blur-3xl -translate-y-1/2 -translate-x-1/2" />

          {/* Welcome Bonus Badge */}
          <div className="flex items-center justify-center gap-3 mb-8 p-4 bg-emerald-400/10 border border-emerald-400/20 rounded-2xl animate-in zoom-in duration-500">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest leading-none">
              5 FREE CREDITS ALLOCATED ON START
            </span>
          </div>

          <Button
            onClick={handleGoogleSignup}
            loading={oauthLoading}
            variant="secondary"
            className="w-full mb-8 font-black text-xs uppercase tracking-widest bg-white text-black hover:bg-gray-100 border-none h-14"
          >
            <Image
              src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
              alt="" width={18} height={18} className="mr-3" unoptimized
            />
            Sign up with Google
          </Button>

          <div className="flex items-center gap-4 mb-8">
            <div className="flex-1 h-px bg-white/5" />
            <span className="text-[10px] font-black text-gray-600 uppercase tracking-widest">OR REGISTER_MANUAL</span>
            <div className="flex-1 h-px bg-white/5" />
          </div>

          <form onSubmit={handleSignup} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Identity Email</label>
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
              <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Secure Key</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl text-white placeholder-gray-600 focus:outline-none focus:border-brand-cyan/50 transition-all font-bold text-sm"
                placeholder="MIN_8_CHARACTERS"
                required
                minLength={8}
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
              Authorize Account
            </Button>
          </form>

          <div className="mt-10 pt-8 border-t border-white/5 space-y-4 text-center">
            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">
              Existing Identity? <Link href="/login" className="text-brand-cyan hover:text-brand-accent ml-1 transition-colors">SignIn Protocol</Link>
            </p>
            <p className="text-[10px] font-bold text-gray-700 uppercase tracking-widest leading-loose">
              BY REGISTERING, YOU ACKNOWLEDGE OUR <Link href="/terms" className="underline hover:text-gray-500">TERMS</Link> AND <Link href="/privacy" className="underline hover:text-gray-500">PRIVACY_POLICY</Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
