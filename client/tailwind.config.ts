import type { Config } from "tailwindcss";
const c = (v: string) => `rgb(var(--${v}) / <alpha-value>)`;
export default {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: {
    colors: { bg: c("bg"), "brand-text": c("brand-text"), line: c("line"), ink: c("ink"), mute: c("mute"), brand: c("brand"), "brand-ink": c("brand-ink") },
    fontFamily: { display: ["var(--font-display)", "sans-serif"], sans: ["var(--font-body)", "sans-serif"] },
  } },
  plugins: [],
} satisfies Config;
