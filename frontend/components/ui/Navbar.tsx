'use client';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Plus, LogOut, Shield, ChevronRight } from 'lucide-react';

export default function Navbar() {
    const pathname = usePathname();
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [user, setUser] = useState<{ full_name?: string; email?: string; avatar_url?: string; is_admin?: boolean } | null>(null);
    const [showDropdown, setShowDropdown] = useState(false);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
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

    // Close menu on navigation
    useEffect(() => {
        setIsMenuOpen(false);
    }, [pathname]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
    };

    const navLinks = [
        { href: '/', label: 'Home' },
        { href: '/creator', label: 'Creator Mode' },
        { href: '/pricing', label: 'Pricing' },
    ];

    const isAdmin = Boolean(user?.is_admin);

    return (
        <>
            <nav className={`fixed top-0 left-0 right-0 z-[60] transition-all duration-500 ${scrolled || isMenuOpen
                ? 'py-3 bg-black/80 backdrop-blur-2xl border-b border-white/5'
                : 'py-5 bg-transparent'
                }`}>
                <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-3 group relative z-[70]">
                        <div className="relative">
                            <Image src="/logo.svg" alt="Proedit" width={32} height={32} className="w-8 h-8" />
                            <div className="absolute inset-0 bg-cyan-500/30 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <span className="text-xl font-bold tracking-tight">
                            <span className="text-white">Pro</span>
                            <span className="bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">edit</span>
                        </span>
                    </Link>

                    {/* Center Nav (Desktop) */}
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
                    <div className="flex items-center gap-2 md:gap-4 relative z-[70]">
                        {isLoggedIn ? (
                            <div className="flex items-center gap-4">
                                <Link
                                    href="/dashboard/upload"
                                    className="hidden sm:flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-cyan-500 to-violet-500 text-sm font-semibold text-white hover:shadow-[0_0_30px_rgba(0,212,255,0.4)] transition-all"
                                >
                                    <Plus className="w-4 h-4" />
                                    Create
                                </Link>

                                <div className="relative">
                                    <button
                                        onClick={() => setShowDropdown(!showDropdown)}
                                        className="flex items-center gap-2 p-1 rounded-full hover:bg-white/10 transition-colors"
                                    >
                                        {user?.avatar_url ? (
                                            <Image src={user.avatar_url} alt="" width={32} height={32} className="w-8 h-8 rounded-full ring-2 ring-white/20" unoptimized />
                                        ) : (
                                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center text-xs font-bold text-white uppercase">
                                                {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                                            </div>
                                        )}
                                    </button>

                                    <AnimatePresence>
                                        {showDropdown && (
                                            <>
                                                <motion.div
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    exit={{ opacity: 0 }}
                                                    className="fixed inset-0 z-40"
                                                    onClick={() => setShowDropdown(false)}
                                                />
                                                <motion.div
                                                    initial={{ opacity: 0, scale: 0.95, y: 10 }}
                                                    animate={{ opacity: 1, scale: 1, y: 0 }}
                                                    exit={{ opacity: 0, scale: 0.95, y: 10 }}
                                                    className="absolute right-0 mt-3 w-64 py-2 glass-lg border-white/10 rounded-2xl shadow-2xl overflow-hidden z-50"
                                                >
                                                    <div className="px-4 py-3 border-b border-white/5 bg-gradient-to-r from-cyan-500/5 to-violet-500/5">
                                                        <p className="text-sm font-bold text-white">{user?.full_name || 'Creator'}</p>
                                                        <p className="text-[10px] text-gray-500 truncate uppercase tracking-widest">{user?.email}</p>
                                                    </div>
                                                    <div className="py-2">
                                                        <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors group">
                                                            <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center group-hover:bg-brand-cyan/20 group-hover:text-brand-cyan transition-colors">
                                                                <ChevronRight className="w-4 h-4" />
                                                            </div>
                                                            Studio Home
                                                        </Link>
                                                        <Link href="/admin" className="flex items-center justify-between px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors group">
                                                            <span className="flex items-center gap-3">
                                                                <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center group-hover:bg-brand-violet/20 group-hover:text-brand-violet transition-colors">
                                                                    <Shield className="w-4 h-4" />
                                                                </div>
                                                                Admin Console
                                                            </span>
                                                            {!isAdmin && (
                                                                <span className="text-[10px] uppercase tracking-widest text-gray-600">Locked</span>
                                                            )}
                                                        </Link>
                                                    </div>
                                                    <div className="border-t border-white/5 py-2">
                                                        <button
                                                            onClick={handleLogout}
                                                            className="flex items-center gap-3 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 w-full transition-colors group"
                                                        >
                                                            <div className="w-8 h-8 rounded-lg bg-red-500/5 flex items-center justify-center group-hover:bg-red-500/20 transition-colors">
                                                                <LogOut className="w-4 h-4" />
                                                            </div>
                                                            Sign Out
                                                        </button>
                                                    </div>
                                                </motion.div>
                                            </>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </div>
                        ) : (
                            <div className="hidden md:flex items-center gap-4">
                                <Link href="/login" className="px-5 py-2.5 text-sm font-medium text-gray-400 hover:text-white transition-colors">
                                    Log in
                                </Link>
                                <Link href="/signup" className="px-5 py-2.5 rounded-full bg-white text-black text-sm font-bold hover:scale-105 transition-transform active:scale-95">
                                    Get Started
                                </Link>
                            </div>
                        )}

                        {/* Mobile Menu Toggle */}
                        <button
                            className="md:hidden w-10 h-10 flex items-center justify-center rounded-xl bg-white/5 border border-white/10 text-white"
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                        >
                            {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                        </button>
                    </div>
                </div>
            </nav>

            {/* Mobile Menu Overlay */}
            <AnimatePresence>
                {isMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="fixed inset-0 z-50 md:hidden pt-24 glass-lg"
                    >
                        <div className="px-6 py-8 space-y-6">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    className="block text-3xl font-bold text-white hover:text-brand-cyan transition-colors"
                                >
                                    {link.label}
                                </Link>
                            ))}

                            {!isLoggedIn && (
                                <div className="pt-8 space-y-4">
                                    <Link href="/login" className="block text-2xl font-bold text-gray-500">Log in</Link>
                                    <Link href="/signup" className="block w-full py-4 rounded-2xl bg-gradient-to-r from-brand-cyan to-brand-violet text-center font-bold text-white text-xl">
                                        Get Started
                                    </Link>
                                </div>
                            )}
                        </div>

                        {/* Decorative Background Elements */}
                        <div className="absolute inset-0 -z-10 pointer-events-none opacity-20">
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-brand-cyan/30 rounded-full blur-[80px]" />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
