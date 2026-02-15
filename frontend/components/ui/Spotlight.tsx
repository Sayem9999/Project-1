"use client";
import { useEffect, useRef } from "react";

/**
 * Interactive spotlight component that tracks the mouse cursor
 * and applies a radial gradient to its parent container.
 */
export default function Spotlight() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const parent = container.parentElement;
    if (!parent) return;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = parent.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      container.style.setProperty("--cursor-x", `${x}px`);
      container.style.setProperty("--cursor-y", `${y}px`);
    };

    parent.addEventListener("mousemove", handleMouseMove);
    return () => parent.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div
      ref={containerRef}
      className="cursor-spotlight opacity-0 group-hover:opacity-100 transition-opacity duration-1000"
      aria-hidden="true"
    />
  );
}
