'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
    const pathname = usePathname();

    const links = [
        { href: '/dashboard', label: 'Projects', icon: '🎬' },
        { href: '/dashboard/library', label: 'Library', icon: '📚' },
        { href: '/dashboard/templates', label: 'Templates', icon: '✨' },
        { href: '/dashboard/settings', label: 'Settings', icon: '⚙️' },
    ];

    return (
        <aside className="w-64 h-screen fixed left-0 top-0 bg-[#0a0a0f]/90 backdrop-blur-xl border-r border-white/5 flex flex-col z-50">
            {/* Brand */}
            <div className="p-6">
                <Link href="/dashboard" className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center text-white font-bold">
                        P
                    </div>
                    <span className="text-xl font-bold text-white tracking-tight">Proedit<span className="text-cyan-400">.ai</span></span>
                </Link>
            </div>

            {/* Nav */}
            <nav className="flex-1 px-4 py-4 space-y-1">
                {links.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive
                                    ? 'bg-gradient-to-r from-cyan-500/20 to-violet-500/20 text-white border border-white/10'
                                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <span className="text-xl">{link.icon}</span>
                            <span className="font-medium text-sm">{link.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Storage Plan */}
            <div className="p-4 m-4 rounded-xl bg-gradient-to-br from-gray-900 to-black border border-white/10">
                <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-medium text-gray-400">Storage</span>
                    <span className="text-xs font-bold text-white">65%</span>
                </div>
                <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-cyan-500 to-violet-500 w-[65%]" />
                </div>
                <p className="text-[10px] text-gray-500 mt-2">13.2 GB of 20 GB used</p>
                <button className="mt-3 w-full py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-medium text-white transition-colors border border-white/5">
                    Upgrade Plan
                </button>
            </div>

            {/* User */}
            <div className="p-4 border-t border-white/5">
                <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-cyan-500 to-violet-500 p-[1px]">
                        <div className="w-full h-full rounded-full bg-black overflow-hidden">
                            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User" className="w-full h-full object-cover" />
                        </div>
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">Sayem User</p>
                        <p className="text-xs text-gray-500 truncate">Pro Plan</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}
