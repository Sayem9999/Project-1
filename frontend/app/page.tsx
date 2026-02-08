'use client';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Play, Wand2, Layers, Zap, Music, Video, Star } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-white selection:bg-brand-cyan/30 overflow-hidden">
      {/* Background Gradients */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-cyan/10 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-brand-violet/10 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute inset-0 bg-grid-white/5 [mask-image:linear-gradient(to_bottom,white,transparent)]" />
      </div>

      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b-0 border-white/5">
        <div className="container mx-auto px-6 h-20 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-cyan to-brand-violet flex items-center justify-center text-white font-bold shadow-lg shadow-brand-cyan/20">
              P
            </div>
            <span className="text-xl font-bold tracking-tight">Proedit<span className="text-brand-cyan">.ai</span></span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium text-gray-400 hover:text-white transition-colors">Login</Link>
            <Link href="/signup">
              <Button size="sm" variant="primary">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 container mx-auto px-6 z-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-brand-cyan mb-8 animate-float">
            <Star className="w-3 h-3 fill-brand-cyan" />
            <span>v4.0 Hollywood Pipeline is Live</span>
          </div>

          <h1 className="text-5xl lg:text-7xl font-bold mb-6 tracking-tight leading-tight">
            AI Video Editing <br />
            <span className="bg-gradient-to-r from-brand-cyan via-brand-violet to-brand-fuchsia bg-clip-text text-transparent">
              Reimagined.
            </span>
          </h1>

          <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Stop removing silence manually. Let our <strong>Hollywood Pipeline</strong> agents
            cut, color, and score your video in minutes.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/signup">
              <Button size="lg" className="group">
                Start Creating Free
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Button size="lg" variant="secondary">
              <Play className="w-4 h-4 mr-2" /> Watch Demo
            </Button>
          </div>
        </motion.div>

        {/* Hero Visual */}
        <div className="mt-20 relative max-w-5xl mx-auto">
          <div className="absolute -inset-1 bg-gradient-to-r from-brand-cyan to-brand-violet rounded-2xl blur opacity-30 animate-pulse-slow" />
          <div className="relative rounded-2xl border border-white/10 bg-surface/50 backdrop-blur-xl overflow-hidden shadow-2xl">
            <img src="/hero-dashboard-mockup.png" alt="Dashboard" className="w-full opacity-80" />
            {/* Fallback visual if image missing */}
            <div className="absolute inset-0 flex items-center justify-center text-gray-600 bg-grid-small-white/5">
              <span className="text-sm border border-white/10 px-4 py-2 rounded-lg bg-black/50 backdrop-blur">Dashboard Preview</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid (Bento) */}
      <section className="py-24 container mx-auto px-6 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold mb-4">Everything you need to create</h2>
          <p className="text-gray-400">Powered by the new LangGraph Orchestration Engine.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[300px]">
          {/* Card 1: Large */}
          <Card className="md:col-span-2 relative group" gradient>
            <div className="absolute top-6 left-6 z-20">
              <div className="w-12 h-12 rounded-lg bg-brand-violet/20 flex items-center justify-center mb-4 text-brand-violet">
                <Wand2 className="w-6 h-6" />
              </div>
              <h3 className="text-2xl font-bold mb-2">AI Director</h3>
              <p className="text-gray-400 max-w-sm">
                Our Director Agent analyzes your footage, understands the mood, and plans the perfect edit structure before cutting a single frame.
              </p>
            </div>
            <div className="absolute right-0 bottom-0 w-1/2 h-full bg-gradient-to-t from-brand-violet/20 to-transparent blur-3xl" />
          </Card>

          {/* Card 2: Tall */}
          <Card className="md:row-span-2 relative overflow-hidden">
            <div className="w-12 h-12 rounded-lg bg-brand-cyan/20 flex items-center justify-center mb-4 text-brand-cyan">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-bold mb-2">Instant Cut</h3>
            <p className="text-gray-400 mb-8">
              Remove silence, filler words, and bad takes automatically with millisecond precision.
            </p>
            <div className="absolute bottom-0 left-0 right-0 h-1/2 bg-gradient-to-t from-brand-cyan/10 to-transparent" />
          </Card>

          {/* Card 3 */}
          <Card>
            <div className="w-12 h-12 rounded-lg bg-brand-fuchsia/20 flex items-center justify-center mb-4 text-brand-fuchsia">
              <Music className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-2">Smart Scoring</h3>
            <p className="text-gray-400 text-sm">
              Audio tracks are auto-selected and synced to the beat of your video.
            </p>
          </Card>

          {/* Card 4 */}
          <Card>
            <div className="w-12 h-12 rounded-lg bg-brand-accent/20 flex items-center justify-center mb-4 text-brand-accent">
              <Video className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-2">MoviePy Engine</h3>
            <p className="text-gray-400 text-sm">
              High-quality rendering with Python-based VFX pipelines.
            </p>
          </Card>
        </div>
      </section>

      {/* CTA */}
      <section className="py-32 container mx-auto px-6 text-center relative z-10">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-4xl lg:text-5xl font-bold mb-6">Ready to upgrade your workflow?</h2>
          <p className="text-xl text-gray-400 mb-10">
            Join thousands of creators saving hours on every video.
          </p>
          <Link href="/signup">
            <Button size="lg" className="w-full sm:w-auto px-12 py-6 text-lg">
              Get Started for Free
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 bg-black/50">
        <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
          <p>© 2026 Proedit.ai. All rights reserved.</p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="#" className="hover:text-white transition-colors">Twitter</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
