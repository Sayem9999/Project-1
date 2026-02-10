'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Home, Upload, Settings, LogOut, Shield } from 'lucide-react';

const navigation = [
    { name: 'Studio Home', href: '/dashboard', icon: Home },
    { name: 'New Project', href: '/dashboard/upload', icon: Upload },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
    { name: 'Admin Console', href: '/admin', icon: Shield },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-4 top-4 bottom-4 w-64 glass-panel rounded-2xl flex flex-col z-50 transition-transform duration-300">
            {/* Brand */}
            <div className="p-8 pb-4">
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-cyan to-brand-violet flex items-center justify-center text-white font-bold shadow-lg shadow-brand-cyan/20 group-hover:shadow-brand-cyan/40 transition-shadow">
                        P
                    </div>
                    <div>
                        <h1 className="text-xl font-bold tracking-tight text-white">Proedit<span className="text-brand-cyan">.ai</span></h1>
                        <p className="text-xs text-brand-violet font-medium tracking-wider">STUDIO</p>
                    </div>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto custom-scrollbar">
                {displayNavigation(navigation, pathname)}
            </nav>

            {/* User / Logout */}
            <div className="p-4 border-t border-white/5 mx-4 mb-2">
                <button
                    onClick={() => {
                        localStorage.removeItem('token');
                        window.location.href = '/login';
                    }}
                    className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all w-full group"
                >
                    <LogOut className="w-5 h-5 group-hover:text-red-400 transition-colors" />
                    <span>Sign Out</span>
                </button>
            </div>
        </aside>
    );
}

function displayNavigation(navItems: typeof navigation, currentPath: string) {
    return navItems.map((item) => {
        const isActive = currentPath === item.href;
        return (
            <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3.5 text-sm font-medium rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive
                        ? "text-white bg-gradient-to-r from-brand-cyan/10 to-transparent border border-brand-cyan/20"
                        : "text-gray-400 hover:text-white hover:bg-white/5"
                    }`}
            >
                {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand-cyan shadow-[0_0_10px_2px_rgba(6,182,212,0.5)]" />
                )}
                <item.icon className={`w-5 h-5 transition-colors ${isActive ? "text-brand-cyan" : "group-hover:text-white"
                    }`} />
                <span>{item.name}</span>
            </Link>
        );
    });
}
