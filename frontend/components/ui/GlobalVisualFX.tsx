'use client';

import { useEffect } from 'react';

export default function GlobalVisualFX() {
  useEffect(() => {
    let raf = 0;
    const handleMove = (event: MouseEvent) => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        document.documentElement.style.setProperty('--cursor-x', `${event.clientX}px`);
        document.documentElement.style.setProperty('--cursor-y', `${event.clientY}px`);
      });
    };

    window.addEventListener('mousemove', handleMove, { passive: true });
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('mousemove', handleMove);
    };
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 z-[5] overflow-hidden" aria-hidden="true">
      <div className="cursor-spotlight" />
      <div className="ambient-orb ambient-orb-cyan" />
      <div className="ambient-orb ambient-orb-violet" />
      <div className="ambient-noise" />
    </div>
  );
}

