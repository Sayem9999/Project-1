'use client';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function Navbar() {
    const pathname = usePathname();
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [user, setUser] = useState<{ full_name?: string; email?: string; avatar_url?: string; is_admin?: boolean } | null>(null);
    const [showDropdown, setShowDropdown] = useState(false);
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('user');
        setIsLoggedIn(!!token);
        if (userData) {
            try { setUser(JSON.parse(userData)); } catch { }
        }

        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
    };

    const navLinks = [
        { href: '/', label: 'Home' },
        { href: '/pricing', label: 'Pricing' },
    ];

    const isAdmin = Boolean(user?.is_admin);

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled
                ? 'py-3 bg-black/80 backdrop-blur-2xl border-b border-white/5'
                : 'py-5 bg-transparent'
            }`}>
            <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="relative">
                        <Image src="/logo.svg" alt="Proedit" width={40} height={40} className="w-10 h-10" />
                        <div className="absolute inset-0 bg-cyan-500/30 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <span className="text-2xl font-bold tracking-tight">
                        <span className="text-white">Pro</span>
                        <span className="bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">edit</span>
                    </span>
                </Link>

                {/* Center Nav */}
                <div className="hidden md:flex items-center gap-1 bg-white/5 rounded-full px-2 py-1.5 border border-white/5">
                    {navLinks.map(link => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`px-5 py-2 rounded-full text-sm font-medium transition-all ${pathname === link.href
                                    ? 'bg-white text-black'
                                    : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            {link.label}
                        </Link>
                    ))}
                </div>

                {/* Right Side */}
                <div className="flex items-center gap-4">
                    {isLoggedIn ? (
                        <>
                            <Link
                                href="/dashboard/upload"
                                className="hidden sm:flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-cyan-500 to-violet-500 text-sm font-semibold text-white hover:shadow-[0_0_30px_rgba(0,212,255,0.4)] transition-all"
                            >
                                <span className="text-lg">+</span>
                                Create
                            </Link>

                            <div className="relative">
                                <button
                                    onClick={() => setShowDropdown(!showDropdown)}
                                    className="flex items-center gap-2 p-1 rounded-full hover:bg-white/10 transition-colors"
                                >
                                    {user?.avatar_url ? (
                                        <Image src={user.avatar_url} alt="" width={36} height={36} className="w-9 h-9 rounded-full ring-2 ring-white/20" unoptimized />
                                    ) : (
                                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center text-sm font-bold text-white">
                                            {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                                        </div>
                                    )}
                                </button>

                                {showDropdown && (
                                    <>
                                        <div className="fixed inset-0" onClick={() => setShowDropdown(false)} />
                                        <div className="absolute right-0 mt-3 w-64 py-2 bg-[#0f0f14] border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
                                            <div className="px-4 py-3 border-b border-white/10 bg-gradient-to-r from-cyan-500/10 to-violet-500/10">
                                                <p className="text-sm font-semibold text-white">{user?.full_name || 'User'}</p>
                                                <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                                            </div>
                                            <div className="py-2">
                                                <Link href="/dashboard/upload" className="flex items-center gap-3 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors">
                                                    <span className="text-xs uppercase tracking-widest text-gray-500">New</span> Project
                                                </Link>
                                                <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors">
                                                    <span className="text-xs uppercase tracking-widest text-gray-500">All</span> My Projects
                                                </Link>
                                                <Link href="/admin" className="flex items-center justify-between px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors">
                                                    <span className="flex items-center gap-3">
                                                        <span className="text-xs uppercase tracking-widest text-gray-500">Admin</span> Console
                                                    </span>
                                                    {!isAdmin && (
                                                        <span className="text-[10px] uppercase tracking-widest text-gray-500">Restricted</span>
                                                    )}
                                                </Link>
                                            </div>
                                            <div className="border-t border-white/10 py-2">
                                                <button
                                                    onClick={handleLogout}
                                                    className="flex items-center gap-3 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 w-full transition-colors"
                                                >
                                                    <span className="text-xs uppercase tracking-widest text-red-400">Exit</span> Sign Out
                                                </button>
                                            </div>
                                        </div>
                                    </>
                                )}
                            </div>
                        </>
                    ) : (
                        <>
                            <Link
                                href="/login"
                                className="px-5 py-2.5 text-sm font-medium text-gray-300 hover:text-white transition-colors"
                            >
                                Log in
                            </Link>
                            <Link
                                href="/signup"
                                className="px-5 py-2.5 rounded-full bg-white text-black text-sm font-semibold hover:bg-gray-100 transition-colors"
                            >
                                Get Started
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}
