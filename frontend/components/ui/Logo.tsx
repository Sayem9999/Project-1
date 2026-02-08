export function Logo() {
    return (
        <div className="flex items-center gap-2 group">
            <div className="relative h-8 w-8 flex items-center justify-center bg-black rounded-lg border border-white/10 overflow-hidden group-hover:border-brand-cyan/50 transition-colors">
                {/* Abstract 'P' shape or geometric logo */}
                <div className="absolute inset-0 bg-gradient-to-br from-brand-violet to-brand-cyan opacity-80 group-hover:opacity-100 transition-opacity"></div>
                <span className="relative z-10 font-bold text-white text-lg">P</span>
            </div>
            <span className="text-xl font-bold tracking-tight text-white group-hover:text-glow transition-all">
                Proedit.com
            </span>
        </div>
    );
}
