'use client';
import { useState } from 'react';
import Link from 'next/link';
import Navbar from '@/components/ui/Navbar';
import Footer from '@/components/ui/Footer';

export default function PricingPage() {
    const [annual, setAnnual] = useState(true);

    const plans = [
        {
            name: 'Free',
            description: 'Perfect for trying out Proedit',
            price: { monthly: 0, annual: 0 },
            features: [
                '5 renders per month',
                '720p output quality',
                'Basic AI agents',
                'Watermark on exports',
                'Community support',
            ],
            cta: 'Start Free',
            href: '/signup',
            popular: false,
        },
        {
            name: 'Pro',
            description: 'For serious content creators',
            price: { monthly: 29, annual: 19 },
            features: [
                '50 renders per month',
                '1080p output quality',
                'All 10 AI agents',
                'No watermark',
                'Priority rendering',
                'Thumbnail generation',
                'Subtitle export',
                'Email support',
            ],
            cta: 'Upgrade to Pro',
            href: '/signup?plan=pro',
            popular: true,
        },
        {
            name: 'Enterprise',
            description: 'For teams and businesses',
            price: { monthly: 99, annual: 79 },
            features: [
                'Unlimited renders',
                '4K output quality',
                'All 10 AI agents',
                'Custom branding',
                'API access',
                'Dedicated support',
                'Team collaboration',
                'Analytics dashboard',
                'SLA guarantee',
            ],
            cta: 'Contact Sales',
            href: '/contact',
            popular: false,
        },
    ];

    return (
        <main className="min-h-screen bg-[#0a0a0f]">
            <Navbar />

            <section className="pt-32 pb-24">
                <div className="container mx-auto px-6">
                    {/* Header */}
                    <div className="text-center mb-12">
                        <span className="inline-block px-4 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-sm font-medium mb-4">
                            Pricing
                        </span>
                        <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
                            Simple, Transparent Pricing
                        </h1>
                        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                            Choose the plan that fits your needs. Upgrade or downgrade anytime.
                        </p>
                    </div>

                    {/* Toggle */}
                    <div className="flex justify-center items-center gap-4 mb-12">
                        <span className={`text-sm ${!annual ? 'text-white' : 'text-gray-500'}`}>Monthly</span>
                        <button
                            onClick={() => setAnnual(!annual)}
                            className={`relative w-14 h-7 rounded-full transition-colors ${annual ? 'bg-cyan-500' : 'bg-gray-700'}`}
                        >
                            <div className={`absolute top-1 w-5 h-5 rounded-full bg-white transition-transform ${annual ? 'left-8' : 'left-1'}`} />
                        </button>
                        <span className={`text-sm ${annual ? 'text-white' : 'text-gray-500'}`}>
                            Annual <span className="text-cyan-400 font-medium">Save 35%</span>
                        </span>
                    </div>

                    {/* Plans */}
                    <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                        {plans.map((plan, i) => (
                            <div
                                key={i}
                                className={`relative p-8 rounded-2xl border transition-all ${plan.popular
                                        ? 'bg-gradient-to-b from-cyan-500/10 to-violet-500/10 border-cyan-500/30 scale-105'
                                        : 'bg-[#12121a] border-white/10 hover:border-white/20'
                                    }`}
                            >
                                {plan.popular && (
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-full text-xs font-semibold text-white">
                                        Most Popular
                                    </div>
                                )}

                                <h3 className="text-xl font-semibold text-white mb-1">{plan.name}</h3>
                                <p className="text-sm text-gray-400 mb-6">{plan.description}</p>

                                <div className="mb-6">
                                    <span className="text-5xl font-bold text-white">
                                        ${annual ? plan.price.annual : plan.price.monthly}
                                    </span>
                                    {plan.price.monthly > 0 && (
                                        <span className="text-gray-400">/month</span>
                                    )}
                                </div>

                                <Link
                                    href={plan.href}
                                    className={`block w-full py-3 rounded-xl text-center font-semibold transition-all ${plan.popular
                                            ? 'bg-gradient-to-r from-cyan-500 to-violet-500 text-white hover:opacity-90'
                                            : 'bg-white/10 text-white hover:bg-white/20'
                                        }`}
                                >
                                    {plan.cta}
                                </Link>

                                <ul className="mt-8 space-y-3">
                                    {plan.features.map((feature, j) => (
                                        <li key={j} className="flex items-center gap-3 text-sm text-gray-300">
                                            <svg className="w-5 h-5 text-cyan-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                            {feature}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>

                    {/* FAQ Teaser */}
                    <div className="text-center mt-16">
                        <p className="text-gray-400">
                            Have questions?{' '}
                            <Link href="/contact" className="text-cyan-400 hover:underline">
                                Contact our team
                            </Link>
                        </p>
                    </div>
                </div>
            </section>

            <Footer />
        </main>
    );
}
