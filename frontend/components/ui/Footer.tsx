export function Footer() {
    return (
        <footer className="border-t border-slate-800 bg-slate-950/50 backdrop-blur-sm">
            <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-4">
                <p className="text-slate-500 text-sm">
                    &copy; {new Date().getFullYear()} Edit.ai Studio. All rights reserved.
                </p>
                <div className="flex gap-6 text-sm text-slate-400">
                    <a href="#" className="hover:text-brand-cyan transition-colors">Privacy</a>
                    <a href="#" className="hover:text-brand-cyan transition-colors">Terms</a>
                    <a href="#" className="hover:text-brand-cyan transition-colors">Contact</a>
                </div>
            </div>
        </footer>
    );
}
