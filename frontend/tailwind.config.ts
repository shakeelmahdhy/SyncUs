import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './app/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        syncus: {
          green: '#00804D',
          blue: '#1E4890',
          lime: '#DBE64C',
          cream: '#F6F8ED',
        },
      },
      fontFamily: {
        sans: ['PP Neue Montreal', 'Inter', 'Arial', 'sans-serif'],
        serif: ['Young Serif', 'Georgia', 'serif'],
      },
      boxShadow: {
        syncus: '0 18px 45px rgba(0, 128, 77, 0.16)',
        card: '0 10px 24px rgba(30, 72, 144, 0.12)',
      },
    },
  },
  plugins: [],
} satisfies Config;
