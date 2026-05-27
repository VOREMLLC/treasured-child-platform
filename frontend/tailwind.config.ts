import type { Config } from "tailwindcss";

// Colour / typography / radius tokens here all reference CSS custom
// properties defined in src/app/globals.css. That keeps globals.css
// the single source of truth for design values; Tailwind classes are
// just convenient names for the same variables.
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Brand blues
        blue: {
          DEFAULT: "var(--blue)",
          deep:    "var(--blue-deep)",
          bright:  "var(--blue-bright)",
          soft:    "var(--blue-soft)",
        },
        navy: "var(--navy)",

        // Accent gold
        gold: {
          DEFAULT: "var(--gold)",
          deep:    "var(--gold-deep)",
        },

        // Dark surfaces — named to avoid Tailwind utility-name clashes
        page:    "var(--bg)",       // bg-page  = page background
        surface: "var(--surface)",  // bg-surface
        card:    "var(--card)",     // bg-card
        line:    "var(--line)",     // border-line

        // Foregrounds
        paper: "var(--text)",       // text-paper = light text on dark
        muted: "var(--muted)",
        ink:   "var(--ink)",

        // Semantic states
        success: "var(--success)",
        danger:  "var(--danger)",
        warning: "var(--warning)",
        info:    "var(--info)",
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body:    ["var(--font-body)"],
      },
      borderRadius: {
        sm:   "8px",
        md:   "12px",
        lg:   "16px",
        xl:   "24px",
        pill: "40px",
      },
      boxShadow: {
        s:       "0 8px 22px -12px rgba(8, 16, 32, .55)",
        DEFAULT: "0 22px 55px -26px rgba(8, 16, 32, .70)",
      },
    },
  },
  plugins: [],
};

export default config;
