'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiRequest, ApiError, clearAuth } from '@/lib/api';

interface Me {
  email: string;
  full_name?: string | null;
  credits: number;
  is_admin: boolean;
}

export default function SettingsPage() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiRequest<Me>('/auth/me', { auth: true });
        setMe(data);
      } catch (err) {
        if (err instanceof ApiError && err.isAuth) {
          clearAuth();
          router.push('/login');
          return;
        }
        setError(err instanceof ApiError ? err.message : 'Failed to load settings');
      }
    };
    load();
  }, [router]);

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">Manage your account and admin access.</p>
      </div>

      {error && (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel rounded-2xl p-6 space-y-3">
          <h2 className="text-lg font-semibold text-white">Account</h2>
          <div className="text-sm text-gray-400">
            <div>Email</div>
            <div className="text-white">{me?.email || 'Loading...'}</div>
          </div>
          <div className="text-sm text-gray-400">
            <div>Credits</div>
            <div className="text-white">{me ? me.credits : '...'}</div>
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white">Admin</h2>
          <p className="text-sm text-gray-400">
            Access system stats, user management, and job monitoring.
          </p>
          <Link
            href="/admin"
            className={`inline-flex items-center justify-center px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${
              me?.is_admin
                ? 'bg-brand-cyan text-black hover:bg-brand-accent'
                : 'bg-white/10 text-gray-400 cursor-not-allowed'
            }`}
            aria-disabled={!me?.is_admin}
          >
            {me?.is_admin ? 'Open Admin Console' : 'Admin Access Required'}
          </Link>
        </div>
      </div>
    </div>
  );
}
