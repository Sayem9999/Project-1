import Link from 'next/link';
import Image from 'next/image';

export default function Footer() {
    return (
        <footer className="bg-black border-t border-white/5">
            <div className="max-w-6xl mx-auto px-6 py-16">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8 lg:gap-16">
                    {/* Brand */}
                    <div className="col-span-2 md:col-span-1">
                        <Link href="/" className="flex items-center gap-3 mb-6">
                            <Image src="/logo.svg" alt="Proedit" width={40} height={40} className="w-10 h-10" />
                            <span className="text-xl font-bold">
                                <span className="text-white">Pro</span>
                                <span className="text-cyan-400">edit</span>
                            </span>
                        </Link>
                        <p className="text-sm text-gray-500 leading-relaxed">
                            AI-powered video editing for creators, marketers, and storytellers.
                        </p>
                    </div>

                    {/* Links */}
                    <div>
                        <h4 className="text-sm font-semibold text-white mb-4">Product</h4>
                        <ul className="space-y-3">
                            {['Features', 'Pricing', 'Changelog', 'Roadmap'].map(item => (
                                <li key={item}>
                                    <Link href={`/${item.toLowerCase()}`} className="text-sm text-gray-500 hover:text-white transition-colors">
                                        {item}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-sm font-semibold text-white mb-4">Company</h4>
                        <ul className="space-y-3">
                            {['About', 'Blog', 'Careers', 'Contact'].map(item => (
                                <li key={item}>
                                    <Link href={`/${item.toLowerCase()}`} className="text-sm text-gray-500 hover:text-white transition-colors">
                                        {item}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-sm font-semibold text-white mb-4">Legal</h4>
                        <ul className="space-y-3">
                            {['Privacy', 'Terms', 'Cookies'].map(item => (
                                <li key={item}>
                                    <Link href={`/${item.toLowerCase()}`} className="text-sm text-gray-500 hover:text-white transition-colors">
                                        {item}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Bottom */}
                <div className="border-t border-white/5 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-sm text-gray-600">
                        © 2024 Proedit.ai. All rights reserved.
                    </p>
                    <div className="flex items-center gap-4">
                        {['Twitter', 'GitHub', 'Discord'].map(social => (
                            <a key={social} href="#" className="text-sm text-gray-600 hover:text-white transition-colors">
                                {social}
                            </a>
                        ))}
                    </div>
                </div>
            </div>
        </footer>
    );
}
