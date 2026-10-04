import type { Config } from "tailwindcss";

// Colour tokens reference CSS custom properties in src/app/globals.css,
// which is the single source of truth (and holds the dark-mode values).
// Tailwind classes are short names for the same variables.
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Off-white, never pure #fff (used for text on blue/navy fills).
        white: "#fffffe",

        blue: {
          DEFAULT: "var(--blue)",
          deep: "var(--blue-deep)",
          ink: "var(--blue-ink)",
          soft: "var(--blue-soft)",
        },
        navy: "var(--navy)",

        gold: {
          DEFAULT: "var(--gold)",
          soft: "var(--gold-soft)",
          text: "var(--gold-text)",
        },

        page: "var(--bg)",
        surface: "var(--surface)",
        card: "var(--card)",
        line: "var(--line)",

        ink: "var(--ink)",
        muted: "var(--muted)",

        success: { DEFAULT: "var(--success)", soft: "var(--success-soft)" },
        danger: { DEFAULT: "var(--danger)", soft: "var(--danger-soft)" },
        warning: { DEFAULT: "var(--warning)", soft: "var(--warning-soft)" },
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
      },
      // Type scale in px: 14 is for captions only; 17 is body.
      fontSize: {
        caption: ["14px", { lineHeight: "1.45" }],
        body: ["17px", { lineHeight: "1.55" }],
        label: ["19px", { lineHeight: "1.35" }],
        title: ["22px", { lineHeight: "1.25" }],
        h3: ["28px", { lineHeight: "1.15" }],
        h2: ["36px", { lineHeight: "1.15" }],
        h1: ["44px", { lineHeight: "1.15" }],
      },
      borderRadius: {
        control: "14px",
        card: "20px",
      },
      boxShadow: {
        s: "0 1px 2px rgba(16,57,95,.06), 0 2px 8px rgba(16,57,95,.06)",
        DEFAULT: "0 8px 24px -8px rgba(16,57,95,.18)",
      },
      keyframes: {
        celebrate: {
          "0%": { transform: "scale(.6)", opacity: "0" },
          "55%": { transform: "scale(1.12)", opacity: "1" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        burst: {
          "0%": { transform: "translate(0,0) scale(.4)", opacity: "1" },
          "100%": {
            transform: "translate(var(--dx), var(--dy)) scale(1)",
            opacity: "0",
          },
        },
        rise: {
          "0%": { transform: "translateY(6px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
      animation: {
        celebrate: "celebrate 600ms ease-out both",
        burst: "burst 600ms ease-out both",
        rise: "rise 200ms ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
