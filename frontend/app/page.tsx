import Navbar from '@/components/ui/Navbar';
import Hero from '@/components/ui/Hero';
import Features from '@/components/ui/Features';
import Footer from '@/components/ui/Footer';
import Link from 'next/link';

export default function Home() {
  return (
    <main className="bg-black">
      <Navbar />
      <Hero />
      <Features />

      {/* How It Works */}
      <section className="py-32 bg-black relative">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-bold text-white mb-6">
              Three steps to magic
            </h2>
            <p className="text-xl text-gray-400">
              Upload, wait, download. It's that simple.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            {[
              { step: '01', title: 'Upload', desc: 'Drop your raw video file', icon: '📤' },
              { step: '02', title: 'AI Magic', desc: '10 agents work in parallel', icon: '✨' },
              { step: '03', title: 'Download', desc: 'Get your polished video', icon: '📥' },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="text-5xl mb-6">{item.icon}</div>
                <div className="text-xs font-mono text-gray-500 mb-2">{item.step}</div>
                <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-32 bg-gradient-to-b from-black via-violet-950/20 to-black relative">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Ready to create?
          </h2>
          <p className="text-xl text-gray-400 mb-10">
            Join thousands of creators using AI to edit videos faster.
          </p>
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 px-10 py-5 rounded-full bg-white text-black text-lg font-semibold hover:shadow-[0_0_50px_rgba(255,255,255,0.3)] transition-all"
          >
            Get started free
            <span>→</span>
          </Link>
          <p className="text-sm text-gray-500 mt-6">No credit card required</p>
        </div>
      </section>

      <Footer />
    </main>
  );
}
