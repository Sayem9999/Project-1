'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { usePathname } from 'next/navigation';
import GlobalVisualFX from '@/components/ui/GlobalVisualFX';
import CommandPalette from '@/components/ui/CommandPalette';
import type { ReactNode } from 'react';

export default function AppEnhancer({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <>
      <GlobalVisualFX />
      <CommandPalette />
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 8, scale: 0.995 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -6, scale: 0.995 }}
          transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
          className="route-transition-root"
        >
          {children}
        </motion.div>
      </AnimatePresence>
    </>
  );
}
