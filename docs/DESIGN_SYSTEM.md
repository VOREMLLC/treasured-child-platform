# Design system: warm, light, simple

> North star: a parent on a mid-range Android phone, on patchy data, can apply
> or pay fees without ever feeling they are "using technology". A child sees
> one big "Continue" button and nothing to figure out.

Tokens live as CSS variables in `frontend/src/app/globals.css` and are mapped
to Tailwind names in `frontend/tailwind.config.ts`. Change values there, never
inline hex in components.

## 1. Principles

1. **One job per screen, one primary button.** Blue is the only action colour.
2. **Start from the customer's next step.** Portal opens on "Continue", pay
   opens on prices, apply success offers "Pay fees".
3. **Never show the machinery.** No references, raw URLs, build notes or
   placeholder warnings in production copy.
4. **Warm, not dry.** Rounded type, gold reserved for rewards and celebration.

## 2. Colour (light default, dark override via `prefers-color-scheme`)

| Token | Hex | Use |
|---|---|---|
| bg | `#F6F8FC` | page |
| surface / card | `#FFFFFE` | cards, sheets |
| line | `#DCE3EE` | borders |
| ink | `#13212F` | body text |
| muted | `#4A5A6E` | secondary text |
| blue | `#1F63C9` | the one action colour |
| blue-deep | `#164A96` | pressed / hover |
| navy | `#10395F` | headings, footer |
| blue-soft | `#E6EFFB` | tint fills |
| gold | `#EFB700` | fills only (with ink text): progress, rewards |
| gold-text | `#7A5B00` | gold-family text |
| success | `#137A4F` / `#E3F5EC` | text / fill |
| danger | `#B42D2D` / `#FBE9E9` | text / fill |
| warning | `#8A5A00` / `#FFF1D6` | text / fill |

Text contrast is at least 4.5:1. Status is never shown by colour alone.

## 3. Type

Baloo 2 (600/700) for headings, Nunito (400/600/800) for body, loaded with
`next/font/google` in `layout.tsx`.

Scale (px): 14 captions only, 17 body, 19 labels and buttons, 22, 28, 36, 44.
Mobile h1 max 36. Body line-height 1.55, headings 1.15 with
`text-wrap: balance`. Sentence case everywhere; no em-dashes in UI copy.

## 4. Space, radius, elevation

- Spacing: 4, 8, 12, 16, 24, 32, 48, 64. Page gutter 16px mobile, 24px sm+,
  max width 1120px.
- Radius: 14px controls, 20px cards, full for pills and progress bars.
- Shadows are navy-tinted: `sm` for cards, `md` for raised sheets. No blur
  effects (costly on low-end Android).

## 5. Motion

150ms `active:scale-[.98]` press feedback, 200ms ease-out state changes, one
600ms celebration when a lesson is finished. Animate transform and opacity
only; everything respects `prefers-reduced-motion`.

## 6. Components (`frontend/src/components/`)

| Component | Purpose |
|---|---|
| `Button` / `ButtonLink` | primary, secondary, ghost; min 48px tall; built-in spinner |
| `Field` | label above, 48px input, hint, error with icon; password show/hide |
| `ChoiceTiles` | large radio cards (class level, fee options with price) |
| `PageHeader` | title plus one line; replaces per-page hero blocks |
| `Skeleton`, `EmptyState`, `StatusViews` | loading, empty, signed-out and error states |
| `ProgressBar` | gold fill with a text label |
| `Nav` + `MobileBottomBar` | desktop top bar; phone bottom bar (public vs portal tabs) |
| `Icon` | one inline SVG set; never text glyphs like ✓ or → |

Data-fetching screens use `lib/useApi.ts` so every page has the same
loading / signed-out / no-access / error / ready states.

## 7. Copy

One label per intent across the site: **Apply now**, **Pay fees**,
**Sign in**, **Continue**. Speak like the school office on WhatsApp: short,
kind, specific ("We'll call or WhatsApp you within 48 hours").

## 8. Accessibility and mobile

Touch targets at least 48px and 8px apart. Visible focus ring on everything
interactive. Test at 375px wide. Bottom bar respects the safe-area inset.

## 9. Still needed from the school

Real campus photos (spot marked in `src/app/page.tsx`), leadership profiles
(marked in `src/app/about/page.tsx`), map location, confirmed fee schedule
(`backend/app/services/fees.py` is the source of truth; `lib/programmes.ts`
mirrors it for display).
