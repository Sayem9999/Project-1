'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Home, Upload, Settings, Shield } from 'lucide-react';
import { motion } from 'framer-motion';

const navigation = [
    { name: 'Home', href: '/dashboard', icon: Home },
    { name: 'Upload', href: '/dashboard/upload', icon: Upload },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
    { name: 'Admin', href: '/admin', icon: Shield },
];

export default function BottomNav() {
    const pathname = usePathname();

    return (
        <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden pb-safe">
            <div className="mx-4 mb-4 glass-lg rounded-2xl p-2 flex items-center justify-around shadow-2xl overflow-hidden relative">
                {/* Active Indicator Glow */}
                <div className="absolute inset-0 bg-gradient-to-t from-brand-cyan/5 to-transparent pointer-events-none" />

                {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className="relative flex flex-col items-center gap-1 p-2 transition-colors group"
                        >
                            {isActive && (
                                <motion.div
                                    layoutId="bottom-nav-pill"
                                    className="absolute inset-0 bg-white/10 rounded-xl"
                                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                />
                            )}

                            <item.icon
                                className={`w-6 h-6 transition-all relative z-10 ${isActive ? "text-brand-cyan scale-110" : "text-gray-500 group-hover:text-gray-300"
                                    }`}
                            />
                            <span className={`text-[10px] font-bold uppercase tracking-widest relative z-10 ${isActive ? "text-brand-cyan" : "text-gray-500"
                                }`}>
                                {item.name}
                            </span>

                            {isActive && (
                                <motion.div
                                    className="absolute -bottom-1 w-1 h-1 bg-brand-cyan rounded-full shadow-[0_0_8px_rgba(6,182,212,0.8)]"
                                    layoutId="bottom-nav-dot"
                                />
                            )}
                        </Link>
                    );
                })}
            </div>
        </nav>
    );
}
