import Navbar from '@/components/ui/Navbar';
import Hero from '@/components/ui/Hero';
import Features from '@/components/ui/Features';
import Footer from '@/components/ui/Footer';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <Hero />
      <Features />

      {/* How It Works Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-sm font-medium mb-4">
              How It Works
            </span>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Three Steps to Magic
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: '01', title: 'Upload', description: 'Drop your raw video file. We support MP4, MOV, AVI, and more.', icon: '📤' },
              { step: '02', title: 'AI Edits', description: '10 AI agents analyze, cut, color, and enhance your footage.', icon: '✨' },
              { step: '03', title: 'Download', description: 'Get your cinematic video ready for YouTube, TikTok, or Instagram.', icon: '🎬' },
            ].map((item, i) => (
              <div key={i} className="relative text-center group">
                {/* Connector Line */}
                {i < 2 && (
                  <div className="hidden md:block absolute top-12 left-1/2 w-full h-px bg-gradient-to-r from-cyan-500/50 to-violet-500/50" />
                )}

                {/* Step Circle */}
                <div className="relative z-10 w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border border-white/10 flex items-center justify-center text-4xl group-hover:scale-110 transition-transform">
                  {item.icon}
                </div>

                <span className="text-sm font-mono text-cyan-400 mb-2 block">{item.step}</span>
                <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-violet-500/10 to-pink-500/10" />
        <div className="container relative z-10 mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Ready to Transform Your Videos?
          </h2>
          <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
            Join thousands of creators using Proedit.ai to create stunning content.
          </p>
          <a
            href="/signup"
            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-xl text-lg font-semibold text-white hover:opacity-90 transition-opacity"
          >
            Get Started Free
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
          <p className="text-sm text-gray-500 mt-4">No credit card required • 5 free renders</p>
        </div>
      </section>

      <Footer />
    </main>
  );
}
