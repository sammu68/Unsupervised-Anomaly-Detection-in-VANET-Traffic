/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                'cyber-navy': '#0f172a',
                'cyber-cyan': '#06b6d4',
                'cyber-red': '#ef4444',
                'cyber-dark': '#020617',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            backgroundImage: {
                'cyber-grid': "radial-gradient(circle, rgba(6,182,212,0.1) 1px, transparent 1px)",
            },
            backgroundSize: {
                'cyber-grid': '20px 20px',
            }
        },
    },
    plugins: [],
}
