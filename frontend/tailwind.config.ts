import type { Config } from 'tailwindcss';

export default {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      },
      colors: {
        obsidian: {
          950: '#020408', // Deep Space
          900: '#050a14', // Void
          800: '#0f172a', // Slate
        },
        brand: {
          cyan: '#06b6d4',     // Cyan 500
          violet: '#8b5cf6',   // Violet 500
          fuchsia: '#d946ef',  // Fuchsia 500
          accent: '#22d3ee',   // Cyan 400
        },
        sidebar: {
          DEFAULT: 'rgba(2, 4, 8, 0.85)',
          border: 'rgba(255, 255, 255, 0.08)',
        }
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'scan': 'scan 4s linear infinite',
        'slide-up': 'slideUp 0.5s ease-out forwards',
        'glow': 'glow 3s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        glow: {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' },
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-obsidian': 'linear-gradient(to bottom, #050a14, #020408)',
      }
    }
  },
  plugins: []
} satisfies Config;
