/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: "#0b0f19",
          800: "#151c2c",
          700: "#1e293b",
        }
      }
    },
  },
  plugins: [],
}
