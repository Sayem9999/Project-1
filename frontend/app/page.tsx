import Link from 'next/link';

export default function Home() {
  return (
    <section className="space-y-8">
      <p className="text-sm uppercase tracking-widest text-cyan-300">Studio-grade automated editing</p>
      <h1 className="text-4xl font-bold leading-tight">Professional human-quality video editing, automated.</h1>
      <p className="max-w-2xl text-slate-300">edit.ai is built for talking-head videos, podcasts, and YouTube creators who care about pacing, sound quality, and final polish.</p>
      <div className="flex gap-4">
        <Link href="/signup" className="rounded bg-cyan-400 px-5 py-3 font-semibold text-slate-950">Start free</Link>
        <Link href="/dashboard/upload" className="rounded border border-slate-700 px-5 py-3">Open Studio</Link>
      </div>
    </section>
  );
}
