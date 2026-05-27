# Design system — the dark dashboard look

> Every page on Treasured Child uses the tokens, type, spacing and
> components in this file. If a page diverges from these tokens, the
> page is wrong, not the system.
>
> The single shared stylesheet that implements this document lives at
> [`assets/css/design-system.css`](../assets/css/design-system.css).
> The sample homepage shell that visibly demonstrates it lives at
> [`design-preview.html`](../design-preview.html) — open it by
> double-clicking, no build step required.

---

## 1. Mission of the look

- **Dark background, light text.** The platform is dark-first across the public site and the LMS. Light surfaces appear only inside cards and form fields.
- **Blue primary, gold accent.** Blue carries trust and academic authority; gold is reserved for emphasis (badges, headings, key CTAs).
- **Generous spacing.** No clutter. Every element gets room to breathe.
- **Sentence case everywhere.** "Apply now", not "APPLY NOW" or "Apply Now".
- **Rounded everything.** Cards, buttons, inputs — soft corners.
- **Mobile-first.** Layouts collapse cleanly at 360 px width.

---

## 2. Colour tokens

The palette is **blue + dark + gold**. Variable names in the stylesheet
mirror this table 1:1.

### 2.1 Brand blues

| Token | Hex | Use |
|---|---|---|
| `--blue` | `#1f63c9` | Primary brand. Buttons, links, key emphasis. |
| `--blue-deep` | `#164a96` | Hover state for primary. Pressed buttons. |
| `--navy` | `#10395f` | Strong headings on light surfaces; deep brand accents. |
| `--blue-bright` | `#2f7fd4` | Mid-blue used in gradients and decorative bands. |
| `--blue-soft` | `#6aa6e6` | Light blue for highlights on dark surfaces. |

### 2.2 Accent gold

| Token | Hex | Use |
|---|---|---|
| `--gold` | `#efb700` | Secondary accent. Reserved for emphasis. |
| `--gold-deep` | `#b88a00` | Gold hover / pressed. |

### 2.3 Dark surfaces (the heart of the dark dashboard)

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#0a1626` | Page background (the darkest layer). |
| `--surface` | `#0f2236` | Section backgrounds raised one step above `--bg`. |
| `--card` | `#142a44` | Cards and panels sitting on `--surface`. |
| `--border` | `#274468` | Subtle dividers and card borders on dark. |

### 2.4 Text on dark

| Token | Hex | Use |
|---|---|---|
| `--text` | `#e8eef7` | Body text on dark surfaces. |
| `--muted` | `#9fb3cd` | Secondary text, captions, helper copy. |
| `--ink` | `#20262a` | Body text on light surfaces (used inside cards if needed). |

### 2.5 Semantic states

| Token | Hex | Use |
|---|---|---|
| `--success` | `#19a86b` | Positive confirmation, paid, completed. |
| `--danger` | `#d24a4a` | Errors, destructive actions, overdue. |
| `--warning` | `#d99a1c` | Caution, pending action. |
| `--info` | `#3b8ad9` | Neutral info banners. |

---

## 3. Typography

Two typefaces, one rule: **headings in Fraunces, everything else in
Hanken Grotesk.** Monospace is system mono — never decorative.

| Role | Family | Weights used |
|---|---|---|
| Display + headings (`h1`–`h3`, hero) | **Fraunces** | 500 / 600 / 700 |
| Body, UI, buttons | **Hanken Grotesk** | 400 / 500 / 600 / 700 |
| Code, references | system monospace | regular |

### Type scale (sentence case, always)

| Style | Size | Line height | Where it's used |
|---|---|---|---|
| `h1` / hero | clamp(34, 5vw, 56) px | 1.08 | Page hero only. One per page. |
| `h2` | clamp(27, 4vw, 40) px | 1.15 | Section headings. |
| `h3` | 19–22 px | 1.25 | Card titles, sub-sections. |
| body | 16–17 px | 1.65 | Default paragraph text. |
| small / caption | 14 px | 1.5 | Helper text, footnotes. |
| eyebrow / kicker | 12 px, uppercase, 0.2 em tracking | 1 | Above section headings. |

Rules:
- **Never ALL CAPS** for headings. The eyebrow is the only uppercased element, and only at 12 px with wide tracking.
- **Line lengths** ≤ 70 characters on body text. Use `max-width: 60ch` for prose blocks.

---

## 4. Spacing scale

Use **only** these values. No `5px`, no `13px`.

```
4   8   12   16   24   32   48   64   96   128
```

| Common pattern | Value |
|---|---|
| Padding inside small buttons | 9 / 16 |
| Padding inside default buttons | 12 / 22 |
| Padding inside cards | 24 (16 on mobile) |
| Gap between cards in a grid | 20–24 |
| Section vertical padding | 64–96 |
| Page side padding | 6 vw (clamps to 24 on small screens) |

---

## 5. Radius

| Token | Pixels | Use |
|---|---|---|
| `--r-sm` | 8 | Small inputs, chips. |
| `--r-md` | 12 | Buttons (square variant), small cards. |
| `--r-lg` | 16 | Default card radius. |
| `--r-xl` | 24 | Hero panels, large feature cards. |
| `--r-pill` | 40 | Pill buttons (the default CTA shape). |

Default CTA shape is **pill (40 px)**.

---

## 6. Elevation

Two shadows, that's it.

| Token | Value | Use |
|---|---|---|
| `--shadow-s` | `0 8px 22px -12px rgba(8,16,32,.55)` | Small lifts: nav bar, small cards on hover. |
| `--shadow` | `0 22px 55px -26px rgba(8,16,32,.7)` | Modal, large card on hover. |

No drop shadows anywhere else. Flat surfaces are the default.

---

## 7. Component inventory

Every reusable UI piece on the platform. Built once in
`design-system.css` (later: as React components), used everywhere.

- **Button** — variants: `btn-primary` (blue), `btn-gold` (gold), `btn-outline` (transparent + border), `btn-ghost` (text only). Sizes: default, `btn-sm`.
- **Card** — default dark card on `--card`, 16 radius, optional hover lift.
- **Stat card** — large numeric, label below, optional trend chip.
- **Programme card** — image / colour-band header, title, body, "Learn more" link.
- **Badge / pill** — small rounded label; semantic colours.
- **Input + label + helper** — full field with error state.
- **Modal** — `--shadow`, dark `--card`, dismiss on overlay click.
- **Toast** — top-right, auto-dismiss, semantic colour.
- **Progress bar** — track on `--surface`, fill in `--blue-bright`.
- **Avatar** — circular, initials on `--blue-deep`.
- **Nav (public)** — sticky top, logo left, tabs centre, CTAs right.
- **Sidebar (portal)** — fixed left, logo + role + tabs; collapses on mobile.
- **Top bar (portal)** — XP / level / streak chips for students; user menu right.
- **Empty state** — icon, headline, helper, single CTA.
- **Spinner** — single dot ring, 20 px default.

---

## 8. Voice

- **Warm, plain, encouraging.** Nigerian English.
- **No jargon to parents.** "Fees" not "tuition disbursement schedule".
- **₦ amounts** are formatted with thousand separators: `₦125,000`, never `125000`.
- **Sentence case for every label, button, heading.** "Apply now", not "Apply Now" or "APPLY NOW".
- **Truth-only copy.** Numbers that appear in the UI come from the database (see [`ENGINEERING_PRINCIPLES.md`](../ENGINEERING_PRINCIPLES.md) §1).

---

## 9. Mobile rules

- **Test 360 px first.** If the page works at 360 px wide, it works everywhere.
- **Single column at ≤ 900 px.** Grids collapse to one column.
- **Nav tabs hide on small screens** — replaced by a hamburger (later); for v1 shell, tabs simply hide and primary CTAs remain.
- **Tap targets ≥ 44 × 44 px.**
- **No horizontal scroll**, ever. If a layout requires it, the layout is wrong.

---

## 10. Accessibility

- **WCAG AA contrast** for text on every surface. Body text on `--bg` and `--surface` is `--text` (`#e8eef7`) — that pairs at AA on both.
- **Visible focus ring** on every interactive element. Default is a 2 px `--blue-bright` outline at 2 px offset.
- **`alt` text on every meaningful image.** Decorative images use `alt=""`.
- **Keyboard navigation** must reach every interactive element in DOM order.
- **Lighthouse accessibility score ≥ 90** on every shipped page.

---

## 11. Logo usage

The school logo is in [`assets/img/logo.png`](../assets/img/logo.png).
It was decoded from the proprietor's demo file —
`treasured_child_school_demo-2.html` — and is the canonical asset until
a higher-resolution version is supplied.

- **Minimum size:** 32 px tall.
- **Always on a white logo badge** in the dark theme. White circle / soft-corner square (14 px radius) with the logo centred. This keeps the logo readable on `--bg`.
- **Clear space:** at least 8 px around the badge on every side.
- **Never recolour the logo.** If a single-colour version is needed, request it from the school.

---

## 12. How to use the stylesheet

The stylesheet at
[`assets/css/design-system.css`](../assets/css/design-system.css)
exposes the tokens as CSS custom properties on `:root` plus a small set
of component classes. To use it on a new page:

```html
<link rel="stylesheet" href="assets/css/design-system.css">
```

Then use the component classes (e.g. `class="btn btn-primary"`,
`class="card"`) and the tokens (e.g.
`style="color: var(--blue)"`) directly. No build step is required for
the static preview; the same tokens will be ported into the Tailwind
config when the Next.js app boots in slice **S1** of
[`BUILD_PLAN.md`](BUILD_PLAN.md).

---

## 13. Changing the design system

When a token changes, the change is:

1. Made in **one** place — `assets/css/design-system.css` and this document, in the same commit.
2. Followed by a quick visual check on [`design-preview.html`](../design-preview.html) to confirm nothing looks broken.
3. Committed with a message like `style(design-system): adjust <token> for <reason>`.

A page that overrides a token locally is a bug. Use the system, or
extend the system; never bypass it.
