/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#080B11",
        card: "#0D131F",
        "card-hover": "#121A2B",
        "card-border": "rgba(34, 211, 238, 0.15)",
        sidebar: "#090D16",
        header: "#080B12",
        brand: {
          cyan: "#00E5FF",
          blue: "#3B82F6",
          dark: "#050914",
        },
        risk: {
          critical: "#F43F5E",
          high: "#F59E0B",
          medium: "#EAB308",
          low: "#14B8A6",
        },
      },
      fontFamily: {
        sans: ["Inter", "Manrope", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
      },
      boxShadow: {
        glow: "0 0 20px rgba(0, 229, 255, 0.15)",
        "glow-cyan": "0 0 15px rgba(6, 182, 212, 0.3)",
        "glow-rose": "0 0 15px rgba(244, 63, 94, 0.3)",
        "glow-amber": "0 0 15px rgba(245, 158, 11, 0.3)",
        "glow-yellow": "0 0 15px rgba(234, 179, 8, 0.3)",
        "glow-teal": "0 0 15px rgba(20, 184, 166, 0.3)",
      },
    },
  },
  plugins: [],
};