# Frontend — Treasured Child platform

Next.js 14 application that serves the public website and the LMS
portal. Pages live under [`src/app/`](src/app/). The visual design
follows [`../docs/DESIGN_SYSTEM.md`](../docs/DESIGN_SYSTEM.md); design
tokens are defined as CSS custom properties in
[`src/app/globals.css`](src/app/globals.css) and exposed as Tailwind
utility classes via [`tailwind.config.ts`](tailwind.config.ts).

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>.

## Layout

```
frontend/
├── package.json
├── tsconfig.json
├── next.config.mjs
├── postcss.config.mjs
├── tailwind.config.ts        # design tokens → Tailwind classes
├── public/
│   └── logo.png              # school logo (canonical asset)
└── src/
    └── app/
        ├── layout.tsx        # root layout, loads globals.css
        ├── page.tsx          # home page
        └── globals.css       # design tokens + Tailwind directives
```

## Design system

- Tokens (colour, type, radius, shadow) are defined in
  [`src/app/globals.css`](src/app/globals.css) as CSS custom
  properties.
- Tailwind classes are thin aliases: `bg-page`, `text-paper`,
  `font-display`, `text-gold`, `border-line`, etc. See the comments in
  [`tailwind.config.ts`](tailwind.config.ts).
- Full reference: [`../docs/DESIGN_SYSTEM.md`](../docs/DESIGN_SYSTEM.md).

## Quality gates

Before committing any change:

```bash
npm run lint    # ESLint (Next's default config)
npm run build   # confirms the app compiles
```

See [`../HARDENING_RULES.md`](../HARDENING_RULES.md) for the full
checkpoint / change / test / commit loop.
