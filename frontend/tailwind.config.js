/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0A0A0A',
        surface: '#141414',
        sidebar: '#111111',
        border: '#1F1F1F',
        primary: {
          DEFAULT: '#F97316',
          hover: '#EA6C0A',
          muted: '#431407',
        },
        error: '#EF4444',
        success: '#22C55E'
      }
    },
  },
  plugins: [],
}
