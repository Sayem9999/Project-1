import Sidebar from '@/components/dashboard/Sidebar';
import TopBar from '@/components/dashboard/TopBar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-obsidian-950 text-white selection:bg-brand-cyan/30 overflow-x-hidden relative">
            {/* Ambient Background */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
                <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-brand-cyan/5 rounded-full blur-[100px] animate-pulse-slow" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] bg-brand-violet/5 rounded-full blur-[100px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
                <div className="absolute inset-0 bg-grid-pattern opacity-20" />
            </div>

            <Sidebar />

            {/* Main Content Area */}
            <div className="pl-72 relative z-10 min-h-screen flex flex-col">
                <TopBar />
                <main className="flex-1 px-8 pb-8">
                    {children}
                </main>
            </div>
        </div>
    );
}
