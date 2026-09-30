/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'netra-bg': '#0f172a',
        'netra-panel': '#1e293b',
        'netra-accent': '#38bdf8',
        'netra-success': '#4ade80',
        'netra-warning': '#fbbf24',
        'netra-danger': '#f87171',
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      animation: {
        'radar-sweep': 'sweep 2s linear infinite',
      },
      keyframes: {
        sweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        ticker: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-33.333333%)' }, // Translates exactly one full set of the duplicated events
        }
      }
    },
  },
  plugins: [],
}

