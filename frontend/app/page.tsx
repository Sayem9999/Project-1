'use client';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Play, Wand2, Layers, Zap, Music, Video, Star, Upload, Activity, Shield, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import NeuralPipeline from '@/components/ui/NeuralPipeline';
import SystemStatusTicker from '@/components/ui/SystemStatusTicker';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-obsidian-950 text-white selection:bg-brand-cyan/30 overflow-hidden relative">
      {/* Ambient Experience Layer */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[60vw] h-[60vw] bg-brand-cyan/10 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[60vw] h-[60vw] bg-brand-violet/10 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute inset-0 bg-grid-pattern opacity-10" />
      </div>

      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/5 transition-all duration-500">
        <div className="max-w-[1400px] mx-auto px-6 h-20 md:h-24 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 md:w-12 md:h-12 rounded-2xl bg-gradient-to-br from-brand-cyan to-brand-violet flex items-center justify-center text-white font-black text-xl shadow-lg shadow-brand-cyan/20 group-hover:rotate-6 transition-transform">
              P
            </div>
            <span className="text-xl md:text-2xl font-black tracking-tighter uppercase">PROEDIT<span className="text-brand-cyan">.AI</span></span>
          </Link>

          <div className="flex items-center gap-6 md:gap-10">
            <div className="hidden md:flex items-center gap-8 text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">
              <Link href="/pricing" className="hover:text-white transition-colors">Economics</Link>
              <Link href="/login" className="hover:text-white transition-colors">Access</Link>
            </div>
            <Link href="/signup">
              <Button size="sm" variant="glow" className="h-12 px-8 font-black text-[10px] uppercase tracking-widest">
                Deploy Now
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-40 pb-24 md:pt-60 md:pb-40 max-w-[1400px] mx-auto px-6 z-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-brand-cyan/10 border border-brand-cyan/30 text-[10px] font-black uppercase tracking-[0.3em] text-brand-cyan mb-10 animate-float">
            <Star className="w-3 h-3 fill-brand-cyan" />
            <span>Hollywood Pipeline v4.0 is live</span>
          </div>

          <h1 className="text-5xl md:text-8xl font-black mb-8 tracking-tighter leading-[0.9] uppercase italic">
            AI Video Editing <br />
            <span className="bg-gradient-to-r from-brand-cyan via-brand-violet to-brand-fuchsia bg-clip-text text-transparent not-italic">
              Directed.
            </span>
          </h1>

          <p className="text-lg md:text-xl text-gray-500 max-w-3xl mx-auto mb-12 font-bold leading-relaxed tracking-tight">
            Upload raw footage. Our studio-grade agents plan, cut, color, and score your edit with surgical precision.
            Witness the future of production.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-16">
            <Link href="/signup" className="w-full sm:w-auto">
              <Button size="lg" variant="glow" className="w-full sm:w-auto h-16 md:h-18 px-12 text-xs font-black uppercase tracking-[0.3em] group">
                Start Free Deployment
                <ArrowRight className="w-5 h-5 ml-4 group-hover:translate-x-2 transition-transform" />
              </Button>
            </Link>
            <Button size="lg" variant="secondary" className="w-full sm:w-auto h-16 md:h-18 px-12 text-xs font-black uppercase tracking-[0.3em] border-white/10 hover:bg-white/5">
              <Play className="w-4 h-4 mr-3 fill-current" /> Watch Showreel
            </Button>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 text-[10px] font-black text-gray-700 uppercase tracking-[0.4em]">
            <span className="flex items-center gap-2">MULTI-AGENT PIPELINE</span>
            <div className="w-1.5 h-1.5 rounded-full bg-brand-cyan opacity-40" />
            <span className="flex items-center gap-2">PLATFORM-READY EXPORTS</span>
            <div className="w-1.5 h-1.5 rounded-full bg-brand-violet opacity-40" />
            <span className="flex items-center gap-2">4K NEURAL RENDER</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-20"
        >
          <SystemStatusTicker />
        </motion.div>

        {/* Hero Visual */}
        <div className="mt-24 relative max-w-6xl mx-auto">
          <div className="absolute -inset-4 bg-gradient-to-r from-brand-cyan/30 to-brand-violet/30 rounded-3xl blur-[80px] opacity-20 animate-pulse-slow" />
          <div className="relative rounded-[48px] border border-white/5 bg-obsidian-900/50 backdrop-blur-3xl overflow-hidden shadow-[0_50px_100px_rgba(0,0,0,0.6)] min-h-[500px] md:min-h-[700px] flex items-center justify-center border-t-white/10 p-4 md:p-10">
            <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-brand-cyan/10 to-transparent pointer-events-none" />
            <NeuralPipeline />
          </div>
        </div>
      </section>

      {/* Technical Workflow */}
      <section className="py-32 max-w-[1400px] mx-auto px-6 relative z-10">
        <div className="text-center mb-20">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Activity className="w-4 h-4 text-brand-cyan" />
            <span className="text-[10px] font-black text-brand-cyan uppercase tracking-[0.3em]">Operational Flow</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black mb-4 uppercase tracking-tighter">Automated Production</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { title: "DEPOSIT_MEDIA", desc: "Drop raw footage. Our vision sub-agents perform instant telemetry analysis.", icon: Upload, color: "text-brand-cyan", bg: "bg-brand-cyan/10" },
            { title: "AGENT_ORCHESTRATION", desc: "Director, Cutter, and Sound agents collaborate on your narrative structure.", icon: Layers, color: "text-brand-violet", bg: "bg-brand-violet/10" },
            { title: "FINAL_EXPORT", desc: "Review your studio-grade cut. Zero watermarks. Full 4K mastery.", icon: Video, color: "text-brand-fuchsia", bg: "bg-brand-fuchsia/10" }
          ].map((step, i) => (
            <div key={i} className="glass-panel p-10 rounded-[40px] border-white/5 hover:border-white/10 transition-colors group">
              <div className={`w-16 h-16 rounded-2xl ${step.bg} flex items-center justify-center mb-8 ${step.color} transition-transform group-hover:scale-110 group-hover:rotate-3`}>
                <step.icon className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-black text-white mb-4 uppercase tracking-widest">{step.title}</h3>
              <p className="text-sm font-bold text-gray-500 leading-relaxed uppercase tracking-tight">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bento Intelligence Grid */}
      <section className="py-24 max-w-[1400px] mx-auto px-6 relative z-10">
        <div className="text-center mb-20 space-y-4">
          <h2 className="text-4xl md:text-6xl font-black uppercase tracking-tighter">Intelligence Suite</h2>
          <p className="text-gray-500 font-bold uppercase tracking-widest text-xs">Powered by the new LangGraph Orchestration Engine.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 auto-rows-[350px]">
          <div className="md:col-span-2 glass-panel p-10 rounded-[48px] border-white/5 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-brand-violet/10 via-transparent to-transparent" />
            <div className="relative z-10 h-full flex flex-col justify-between">
              <div className="space-y-6">
                <div className="w-16 h-16 rounded-2xl bg-brand-violet/20 flex items-center justify-center text-brand-violet">
                  <Wand2 className="w-8 h-8" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-3xl font-black text-white uppercase tracking-tight">AI Lead Director</h3>
                  <p className="text-gray-500 max-w-sm font-bold uppercase tracking-tight leading-relaxed">
                    The Director Agent analyzes your footage, understands the conceptual mood, and plans the perfect edit structure before cutting a single frame.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 text-[10px] font-black text-brand-violet uppercase tracking-widest group-hover:translate-x-2 transition-transform">
                View Intelligence Logs <ArrowRight className="w-4 h-4" />
              </div>
            </div>
          </div>

          <div className="md:row-span-2 glass-panel p-10 rounded-[48px] border-white/5 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-t from-brand-cyan/10 via-transparent to-transparent" />
            <div className="relative z-10 h-full flex flex-col justify-between">
              <div className="space-y-6">
                <div className="w-16 h-16 rounded-2xl bg-brand-cyan/20 flex items-center justify-center text-brand-cyan">
                  <Zap className="w-8 h-8" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-3xl font-black text-white uppercase tracking-tight leading-none">High-Speed Precision</h3>
                  <p className="text-gray-500 font-bold uppercase tracking-tight leading-relaxed mt-4">
                    Remove silence, filler words, and dead air automatically with millisecond neural precision. Built for high-frequency content creators.
                  </p>
                </div>
              </div>
              <div className="absolute bottom-10 right-10">
                <Sparkles className="w-20 h-20 text-brand-cyan/10 animate-pulse" />
              </div>
            </div>
          </div>

          <div className="glass-panel p-10 rounded-[48px] border-white/5 group">
            <div className="w-14 h-14 rounded-2xl bg-brand-fuchsia/20 flex items-center justify-center mb-8 text-brand-fuchsia">
              <Music className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-black text-white uppercase tracking-widest mb-4">Neural Score</h3>
            <p className="text-xs font-black text-gray-500 uppercase tracking-widest leading-loose">
              Audio tracks are neurally aligned and beat-synced to your visual pacing automatically.
            </p>
          </div>

          <div className="glass-panel p-10 rounded-[48px] border-white/5 group">
            <div className="w-14 h-14 rounded-2xl bg-brand-accent/20 flex items-center justify-center mb-8 text-brand-accent">
              <Video className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-black text-white uppercase tracking-widest mb-4">Master Render</h3>
            <p className="text-xs font-black text-gray-500 uppercase tracking-widest leading-loose">
              Cinematic grading and multi-platform optimization for YouTube, TikTok, and Instagram Reel nodes.
            </p>
          </div>
        </div>
      </section>

      {/* Master CTA */}
      <section className="py-40 max-w-4xl mx-auto px-6 text-center relative z-10">
        <div className="glass-panel p-16 md:p-24 rounded-[64px] border-white/10 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-brand-cyan/10 to-brand-violet/10" />
          <div className="relative z-10 space-y-10">
            <h2 className="text-4xl md:text-6xl font-black uppercase tracking-tighter">Ready for Deployment?</h2>
            <p className="text-lg md:text-xl text-gray-500 font-bold uppercase tracking-tight max-w-2xl mx-auto leading-relaxed">
              Initialize your first project and experience the velocity of AI-directed production.
              5 free credits allocated to all new nodes.
            </p>
            <Link href="/signup" className="block">
              <Button size="lg" variant="glow" className="h-20 px-16 text-xs font-black uppercase tracking-[0.4em] shadow-[0_20px_50px_rgba(6,182,212,0.3)]">
                Initialize Account Access
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Technical Footer */}
      <footer className="border-t border-white/5 py-16 bg-obsidian-950/80 relative z-10">
        <div className="max-w-[1400px] mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-10">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-[10px] font-black italic">P</div>
              <span className="text-[10px] font-black uppercase tracking-[0.5em] text-gray-600">PROEDIT.AI // 2026.SYS</span>
            </div>

            <div className="flex gap-10 text-[10px] font-black uppercase tracking-[0.3em] text-gray-600">
              <span className="flex items-center gap-2"><Shield className="w-3 h-3" /> Encrypted</span>
              <span className="flex items-center gap-2"><Star className="w-3 h-3" /> Priority</span>
              <span className="flex items-center gap-2"><Zap className="w-3 h-3" /> 0ms Latency</span>
            </div>

            <div className="flex gap-8 text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Social</a>
            </div>
          </div>
          <div className="mt-12 text-center">
            <p className="text-[9px] font-bold text-gray-800 uppercase tracking-widest">Global Operations Node: 50.116.32.1 // Platform Version: 4.0.2 Stable Build</p>
          </div>
        </div>
      </footer>
    </div >
  );
}
