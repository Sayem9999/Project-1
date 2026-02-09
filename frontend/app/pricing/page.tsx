'use client';
import { useState } from 'react';
import { Check } from 'lucide-react';
import Sidebar from '@/components/dashboard/Sidebar';
import TopBar from '@/components/dashboard/TopBar';
import { API_BASE } from '@/lib/api';

export default function PricingPage() {
    const [loading, setLoading] = useState(false);

    const handlePurchase = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE}/payments/create-checkout-session`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Checkout failed');
            if (data.url) {
                window.location.href = data.url;
            } else {
                alert('Checkout failed');
            }
        } catch (error) {
            console.error('Purchase error:', error);
            alert('Something went wrong');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0f] text-white selection:bg-cyan-500/30">
            <Sidebar />
            <TopBar />

            <main className="ml-64 p-12 relative z-10">
                <div className="max-w-4xl mx-auto text-center">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent mb-4">
                        Upgrade Your Creativity
                    </h1>
                    <p className="text-gray-400 text-lg mb-12">
                        Get access to the Hollywood Pipeline (v4.0) with Pro Credits.
                    </p>

                    <div className="grid md:grid-cols-2 gap-8 items-center">
                        {/* Free Tier Info */}
                        <div className="p-8 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-sm grayscale opacity-75">
                            <h3 className="text-2xl font-bold mb-2">Started</h3>
                            <div className="text-4xl font-bold mb-6">$0</div>
                            <ul className="space-y-4 text-left text-gray-400 mb-8">
                                <li className="flex gap-2"><Check size={18} /> Standard Pipeline (v3)</li>
                                <li className="flex gap-2"><Check size={18} /> basic edits</li>
                                <li className="flex gap-2"><Check size={18} /> Watermarked</li>
                            </ul>
                            <div className="text-sm font-medium text-gray-500">
                                Use your monthly free credits
                            </div>
                        </div>

                        {/* Pro Pack */}
                        <div className="p-8 rounded-2xl border border-cyan-500/30 bg-gradient-to-b from-cyan-900/10 to-transparent relative overflow-hidden">
                            <div className="absolute top-0 right-0 bg-cyan-500 text-black text-xs font-bold px-3 py-1 rounded-bl-lg">
                                POPULAR
                            </div>
                            <h3 className="text-2xl font-bold mb-2 text-cyan-400">Pro Pack</h3>
                            <div className="text-4xl font-bold mb-6">$10 <span className="text-sm text-gray-400 font-normal">/ 10 credits</span></div>
                            <ul className="space-y-4 text-left text-gray-300 mb-8">
                                <li className="flex gap-2 items-center"><Check size={18} className="text-cyan-400" /> Hollywood Pipeline (v4.0)</li>
                                <li className="flex gap-2 items-center"><Check size={18} className="text-cyan-400" /> 5 Pro Edits (2 Credits/each)</li>
                                <li className="flex gap-2 items-center"><Check size={18} className="text-cyan-400" /> No Watermark</li>
                                <li className="flex gap-2 items-center"><Check size={18} className="text-cyan-400" /> Priority Rendering</li>
                            </ul>
                            <button
                                onClick={handlePurchase}
                                disabled={loading}
                                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-500 hover:opacity-90 transition-opacity font-bold text-lg disabled:opacity-50"
                            >
                                {loading ? 'Processing...' : 'Buy 10 Credits'}
                            </button>
                            <p className="text-xs text-gray-500 mt-4">Secure payment via Stripe</p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
