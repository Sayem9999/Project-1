'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Compass, LayoutDashboard, Shield, Sparkles, Upload, User } from 'lucide-react';
import type { ComponentType } from 'react';

type CommandItem = {
  id: string;
  label: string;
  description: string;
  href: string;
  icon: ComponentType<{ className?: string }>;
  keywords: string[];
};

const COMMANDS: CommandItem[] = [
  {
    id: 'upload',
    label: 'New Project Upload',
    description: 'Start a fresh AI edit from your dashboard.',
    href: '/dashboard/upload',
    icon: Upload,
    keywords: ['new', 'upload', 'project', 'create'],
  },
  {
    id: 'dashboard',
    label: 'Open Dashboard',
    description: 'View your jobs and project activity.',
    href: '/dashboard',
    icon: LayoutDashboard,
    keywords: ['dashboard', 'jobs', 'projects', 'home'],
  },
  {
    id: 'admin',
    label: 'Admin Console',
    description: 'Inspect system health, users, and jobs.',
    href: '/admin',
    icon: Shield,
    keywords: ['admin', 'ops', 'health', 'system'],
  },
  {
    id: 'creator',
    label: 'Creator Studio',
    description: 'Generate and iterate creative content.',
    href: '/creator',
    icon: Sparkles,
    keywords: ['creator', 'studio', 'ideas'],
  },
  {
    id: 'pricing',
    label: 'Pricing',
    description: 'Check plan tiers and limits.',
    href: '/pricing',
    icon: Compass,
    keywords: ['pricing', 'plans', 'credits', 'billing'],
  },
  {
    id: 'login',
    label: 'Sign In',
    description: 'Switch account or continue session.',
    href: '/login',
    icon: User,
    keywords: ['login', 'signin', 'account'],
  },
];

export default function CommandPalette() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(0);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return COMMANDS;
    return COMMANDS.filter((item) => {
      const haystack = `${item.label} ${item.description} ${item.keywords.join(' ')}`.toLowerCase();
      return haystack.includes(q);
    });
  }, [query]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const isToggle = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k';
      if (isToggle) {
        event.preventDefault();
        setOpen((prev) => !prev);
      } else if (event.key === 'Escape') {
        setOpen(false);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  useEffect(() => {
    if (!open) return;
    setSelected(0);
    const timer = window.setTimeout(() => inputRef.current?.focus(), 30);
    return () => window.clearTimeout(timer);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (!filtered.length) return;
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        setSelected((prev) => (prev + 1) % filtered.length);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        setSelected((prev) => (prev - 1 + filtered.length) % filtered.length);
      } else if (event.key === 'Enter') {
        event.preventDefault();
        const item = filtered[selected];
        if (item) {
          setOpen(false);
          setQuery('');
          router.push(item.href);
        }
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open, filtered, selected, router]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.button
            type="button"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[80] bg-black/55 backdrop-blur-sm"
            onClick={() => setOpen(false)}
            aria-label="Close command palette"
          />
          <motion.div
            initial={{ opacity: 0, y: -16, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -12, scale: 0.98 }}
            transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
            className="fixed z-[90] left-1/2 top-[14vh] w-[min(720px,92vw)] -translate-x-1/2 rounded-2xl border border-white/15 bg-slate-950/90 shadow-2xl shadow-black/70 overflow-hidden"
          >
            <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10 bg-white/[0.03]">
              <span className="text-xs px-2 py-1 rounded-md border border-white/15 text-brand-cyan">Ctrl/Cmd + K</span>
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Jump to page, feature, or workflow..."
                className="w-full bg-transparent text-sm text-white placeholder:text-gray-500 outline-none"
              />
            </div>
            <div className="max-h-[420px] overflow-y-auto py-2">
              {filtered.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-gray-400">No matching actions.</div>
              ) : (
                filtered.map((item, idx) => {
                  const Icon = item.icon;
                  const active = idx === selected;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onMouseEnter={() => setSelected(idx)}
                      onClick={() => {
                        setOpen(false);
                        setQuery('');
                        router.push(item.href);
                      }}
                      className={`w-full text-left px-4 py-3 flex items-center gap-3 transition-colors ${
                        active ? 'bg-brand-cyan/15' : 'hover:bg-white/5'
                      }`}
                    >
                      <div className={`w-9 h-9 rounded-lg border flex items-center justify-center ${
                        active ? 'border-brand-cyan/40 text-brand-cyan' : 'border-white/10 text-gray-400'
                      }`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-white">{item.label}</div>
                        <div className="text-xs text-gray-400">{item.description}</div>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
