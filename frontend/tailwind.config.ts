import type { Config } from 'tailwindcss';

export default {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#030712', // Darker than slate-950
        brand: {
          cyan: '#06b6d4',
          magenta: '#d946ef',
          violet: '#8b5cf6',
          dark: '#0f172a',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #06b6d4' },
          '100%': { boxShadow: '0 0 20px #06b6d4, 0 0 10px #d946ef' },
        }
      }
    }
  },
  plugins: []
} satisfies Config;
