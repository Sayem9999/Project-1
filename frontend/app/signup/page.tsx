'use client';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch } from '@/lib/api';

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  async function submit(e: FormEvent) {
    e.preventDefault();
    try {
      const res = await apiFetch('/auth/signup', { method: 'POST', body: JSON.stringify({ email, password }) });
      if (!res.ok) {
        const errText = await res.text();
        if (res.status === 400 && errText.includes("already registered")) {
          setError("Account already exists. Redirecting to login...");
          setTimeout(() => router.push('/login'), 2000);
          return;
        }
        return setError(`Signup failed (Status ${res.status}): ${errText}`);
      }
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      router.push('/dashboard/upload');
    } catch (e) {
      setError(`Network error: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  return <form onSubmit={submit} className="mx-auto max-w-md space-y-4"><h1 className="text-2xl font-semibold">Create account</h1><input className="w-full rounded bg-slate-900 p-3" placeholder="Email" onChange={(e) => setEmail(e.target.value)} /><input type="password" className="w-full rounded bg-slate-900 p-3" placeholder="Password" onChange={(e) => setPassword(e.target.value)} /><button className="w-full rounded bg-cyan-400 p-3 font-semibold text-slate-950">Create account</button><p className="text-red-400">{error}</p></form>;
}
