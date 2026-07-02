/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#7C3AED',
        secondary: '#A78BFA',
        accent: '#F43F5E',
        background: '#0F0F23',
        foreground: '#E2E8F0',
        muted: '#27273B',
        border: '#4C1D95',
        destructive: '#EF4444',
        ring: '#7C3AED',
      },
      fontFamily: {
        heading: ['Orbitron', 'sans-serif'],
        body: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-neon': 'pulseNeon 2s ease-in-out infinite',
        'glow': 'glow 3s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'typing': 'typing 1.5s steps(4) infinite',
      },
      keyframes: {
        pulseNeon: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        glow: {
          'from': { boxShadow: '0 0 5px #7C3AED, 0 0 10px #7C3AED' },
          'to': { boxShadow: '0 0 20px #7C3AED, 0 0 30px #A78BFA' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        fadeIn: {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
        slideUp: {
          'from': { opacity: '0', transform: 'translateY(10px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
        typing: {
          '0%, 100%': { opacity: '0.2' },
          '50%': { opacity: '1' },
        },
      }
    },
  },
  plugins: [],
}