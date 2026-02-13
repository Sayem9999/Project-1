import GlobalVisualFX from '@/components/ui/GlobalVisualFX';
import CommandPalette from '@/components/ui/CommandPalette';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import type { ReactNode } from 'react';

export default function AppEnhancer({ children }: { children: ReactNode }) {
  return (
    <>
      <GlobalVisualFX />
      <CommandPalette />
      <ErrorBoundary>
        <div className="route-root">
          {children}
        </div>
      </ErrorBoundary>
    </>
  );
}
