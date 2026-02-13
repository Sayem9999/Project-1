import Sidebar from '@/components/dashboard/Sidebar';
import TopBar from '@/components/dashboard/TopBar';
import BottomNav from '@/components/ui/BottomNav';

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

            {/* Main Content Area - Dynamic Padding */}
            <div className="pl-0 md:pl-72 relative z-10 min-h-screen flex flex-col pb-24 md:pb-0">
                <TopBar />
                <main className="flex-1 px-4 md:px-8 pb-8">
                    {children}
                </main>
            </div>

            <BottomNav />
        </div>
    );
}
