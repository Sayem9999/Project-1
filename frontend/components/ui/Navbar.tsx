'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';

export function Navbar() {
    const [isOpen, setIsOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const pathname = usePathname();

    // Handle scroll effect
    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navLinks = [
        { name: 'Features', href: '/#features' },
        { name: 'Pricing', href: '/#pricing' },
        { name: 'Login', href: '/login' },
    ];

    return (
        <nav
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled || isOpen ? 'bg-slate-950/80 backdrop-blur-lg border-b border-white/5' : 'bg-transparent border-transparent'
                }`}
        >
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="flex h-20 items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 group">
                        <div className="h-8 w-8 rounded bg-gradient-to-br from-brand-cyan to-brand-violet group-hover:shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300"></div>
                        <span className="text-xl font-bold tracking-tight text-white group-hover:text-glow transition-all">
                            edit.ai
                        </span>
                    </Link>

                    {/* Desktop Nav */}
                    <div className="hidden md:flex items-center gap-8">
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                href={link.href}
                                className={`text-sm font-medium transition-colors hover:text-brand-cyan ${pathname === link.href ? 'text-brand-cyan' : 'text-slate-300'
                                    }`}
                            >
                                {link.name}
                            </Link>
                        ))}
                        <Link
                            href="/signup"
                            className="btn-primary text-sm px-5 py-2.5 rounded-full"
                        >
                            Start Creating
                        </Link>
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="md:hidden p-2 text-slate-300 hover:text-white"
                    >
                        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            {isOpen ? (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            )}
                        </svg>
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            {isOpen && (
                <div className="md:hidden bg-slate-950/95 backdrop-blur-xl border-b border-white/10">
                    <div className="space-y-1 px-4 pb-6 pt-2">
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                href={link.href}
                                onClick={() => setIsOpen(false)}
                                className="block py-3 text-base font-medium text-slate-300 hover:text-brand-cyan border-b border-white/5"
                            >
                                {link.name}
                            </Link>
                        ))}
                        <Link
                            href="/signup"
                            onClick={() => setIsOpen(false)}
                            className="block mt-4 text-center btn-primary w-full py-3 rounded-lg"
                        >
                            Start Creating
                        </Link>
                    </div>
                </div>
            )}
        </nav>
    );
}
