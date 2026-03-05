/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./index.html",
        "./ui/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0f1115",
                surface: "#1a1d23",
                border: "#2a2e37",
                accent: "#6366f1",
                primary: "#df912a",
                secondary: "#10b981",
                error: "#ef4444",
                text: "#e5e7eb",
                "text-dim": "#9ca3af"
            },
            fontFamily: {
                sans: ["Inter", "system-ui", "sans-serif"],
                mono: ["JetBrains Mono", "monospace"]
            }
        },
    },
    plugins: [],
}
