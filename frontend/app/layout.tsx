import './globals.css';
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
          {children}
        </ToastProvider>
      </body>
    </html>
  );
}
