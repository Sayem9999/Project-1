'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function Navbar() {
    const pathname = usePathname();
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [user, setUser] = useState<{ name?: string; email?: string; avatar_url?: string } | null>(null);
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

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-[#0a0a0f]/90 backdrop-blur-xl border-b border-white/10' : 'bg-transparent'
            }`}>
            <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 24px' }}>
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 group">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center text-white text-sm">
                            ▶
                        </div>
                        <span className="text-xl font-bold text-white group-hover:text-cyan-400 transition-colors">
                            Proedit<span className="text-cyan-400">.ai</span>
                        </span>
                    </Link>

                    {/* Center Nav Links */}
                    <div className="hidden md:flex items-center gap-1">
                        {navLinks.map(link => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${pathname === link.href
                                        ? 'text-cyan-400 bg-cyan-400/10'
                                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                                    }`}
                            >
                                {link.label}
                            </Link>
                        ))}
                    </div>

                    {/* Right Side */}
                    <div className="flex items-center gap-3">
                        {isLoggedIn ? (
                            <>
                                <Link
                                    href="/dashboard/upload"
                                    className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg text-sm font-semibold text-white hover:opacity-90 transition-opacity"
                                >
                                    + New Project
                                </Link>

                                {/* User Menu */}
                                <div className="relative">
                                    <button
                                        onClick={() => setShowDropdown(!showDropdown)}
                                        className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-white/5 transition-colors"
                                    >
                                        {user?.avatar_url ? (
                                            <img src={user.avatar_url} alt="" className="w-8 h-8 rounded-full" />
                                        ) : (
                                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center text-sm font-bold text-white">
                                                {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                                            </div>
                                        )}
                                        <span className="text-gray-400">▼</span>
                                    </button>

                                    {showDropdown && (
                                        <div className="absolute right-0 mt-2 w-56 py-2 bg-[#1a1a26] border border-white/10 rounded-xl shadow-2xl">
                                            <div className="px-4 py-2 border-b border-white/10">
                                                <p className="text-sm font-medium text-white">{user?.name || 'User'}</p>
                                                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                                            </div>
                                            <Link href="/dashboard/upload" className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-300 hover:bg-white/5 transition-colors">
                                                📤 Upload Video
                                            </Link>
                                            <Link href="/dashboard" className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-300 hover:bg-white/5 transition-colors">
                                                📁 My Projects
                                            </Link>
                                            <div className="border-t border-white/10 mt-2 pt-2">
                                                <button
                                                    onClick={handleLogout}
                                                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 w-full transition-colors"
                                                >
                                                    🚪 Sign Out
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : (
                            <>
                                <Link
                                    href="/login"
                                    className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors"
                                >
                                    Sign In
                                </Link>
                                <Link
                                    href="/signup"
                                    className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg text-sm font-semibold text-white hover:opacity-90 transition-opacity"
                                >
                                    Get Started Free
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
