import './globals.css';
import { Toaster } from 'sonner';
import { ToastProvider } from '@/components/ui/Toast';
import SystemBanner from '@/components/ui/SystemBanner';

export const metadata = {
  title: 'Proedit.ai - AI Video Editing',
  description: 'Transform your raw footage into cinematic content with AI-powered editing.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ToastProvider>
          <SystemBanner />
          <Toaster richColors position="top-right" theme="dark" />
          {children}
        </ToastProvider>
      </body>
    </html>
  );
}
