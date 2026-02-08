import Link from 'next/link';

export function Hero() {
    return (
        <div className="relative isolate pt-14">
            {/* Background Gradients */}
            <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
                <div
                    className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-brand-cyan to-brand-violet opacity-20 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
                    style={{ clipPath: 'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)' }}
                />
            </div>

            <div className="py-24 sm:py-32 lg:pb-40">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-4xl text-center">
                        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl text-glow animate-float">
                            Professional Video Editing, <br />
                            <span className="text-gradient">Automated by AI</span>
                        </h1>
                        <p className="mt-6 text-lg leading-8 text-slate-300">
                            Transform raw footage into studio-quality content in minutes.
                            Our AI Director, Colorist, and Audio Engineers work together to polish your video to perfection.
                        </p>
                        <div className="mt-10 flex items-center justify-center gap-x-6">
                            <Link href="/signup" className="btn-primary text-lg px-8 py-4">
                                Start Production
                            </Link>
                            <Link href="/login" className="text-sm font-semibold leading-6 text-white hover:text-brand-cyan transition-colors">
                                Log in <span aria-hidden="true">→</span>
                            </Link>
                        </div>
                    </div>

                    {/* Mockup / Visual */}
                    <div className="mt-16 flow-root sm:mt-24">
                        <div className="-m-2 rounded-xl bg-white/5 p-2 ring-1 ring-inset ring-white/10 lg:-m-4 lg:rounded-2xl lg:p-4 hover:ring-brand-cyan/30 transition-all duration-500">
                            <div className="rounded-md bg-slate-950/50 shadow-2xl ring-1 ring-white/10 overflow-hidden aspect-video relative group">
                                {/* Abstract UI Representation */}
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="w-24 h-24 rounded-full bg-slate-800/50 flex items-center justify-center group-hover:scale-110 transition-transform duration-300 border border-white/10 backdrop-blur-sm">
                                        <svg className="w-10 h-10 text-brand-cyan ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
                                    </div>
                                </div>
                                <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-brand-cyan to-brand-violet animate-scan"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
