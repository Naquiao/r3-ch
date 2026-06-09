---
version: alpha
name: Bugster
description: >-
  Brand & product design system for Bugster — an autonomous QA agent that lives
  inside your pull requests. Aesthetic: "ink on warm paper", a playful technical
  blueprint. Crisp 1px ink hairlines, generous rounding, flat candy accents, and
  hard offset "sticker" shadows instead of soft blur.
colors:
  primary: "#058BFF"
  primary-ink: "#0070D1"
  on-primary: "#FFFFFF"
  ink: "#050505"
  ink-muted: "#6B6B6B"
  paper: "#F6F2EE"
  surface: "#FBFBFA"
  white: "#FFFFFF"
  sand: "#E5DED5"
  purple: "#B095FA"
  pink: "#FFCEE4"
  coral: "#FD7876"
  lime: "#F4FFC9"
  border: "{colors.ink}"
  success: "#1F8A5B"
  danger: "#E5483A"
typography:
  display:
    fontFamily: Geist Mono
    fontSize: 7.5rem
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.02em"
  h1:
    fontFamily: Geist Mono
    fontSize: 4rem
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  h2:
    fontFamily: Geist Mono
    fontSize: 3rem
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.015em"
  h3:
    fontFamily: Geist Mono
    fontSize: 2.125rem
    fontWeight: 600
    lineHeight: 1.15
  eyebrow:
    fontFamily: Geist Mono
    fontSize: 0.8125rem
    fontWeight: 500
    lineHeight: 1.15
    letterSpacing: "0.12em"
  label:
    fontFamily: Geist Mono
    fontSize: 0.75rem
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "0.04em"
  body-lg:
    fontFamily: Figtree
    fontSize: 1.25rem
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: Figtree
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: Figtree
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5
  code:
    fontFamily: Geist Mono
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5
rounded:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  2xl: 32px
  pill: 999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "12px 20px"
  button-primary-hover:
    backgroundColor: "{colors.primary-ink}"
  button-primary-active:
    backgroundColor: "{colors.primary-ink}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "12px 20px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "12px 18px"
  input:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    padding: "0 13px"
    height: 46px
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xl}"
    padding: 24px
  badge-success:
    backgroundColor: "{colors.lime}"
    textColor: "{colors.success}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "3px 8px"
  badge-alert:
    backgroundColor: "{colors.coral}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "3px 8px"
  tag:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "5px 12px"
  keyword:
    backgroundColor: "{colors.lime}"
    textColor: "{colors.ink}"
    typography: "{typography.code}"
    rounded: "{rounded.xs}"
    padding: "1px 8px"
  node-handle:
    backgroundColor: "{colors.lime}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xs}"
    size: 26px
---

## Overview

Bugster is an **autonomous QA agent** built for fast-moving, product-minded
developers. The brand should feel **sharp, playful and deliberately crafted** —
classic-UI nostalgia rendered with crisp hairlines and candy accents.

The governing metaphor is **ink on warm paper**: near-black ink drawn on an
off-white "paper" page, the way a technical blueprint or a folder of printouts
looks. Almost everything is an outline. Color arrives in small, confident doses.

Voice matches the visuals — a senior engineer who is concise and a little
playful, never corporate. Speak to the developer as **"you"**; the product is
**"Bugster"** (or "he", via the mascot). Headlines are 2–6 words. The brand
loves *"no ___"* constructions — *"no config, no test files, no babysitting."*
Sentence case for prose; **UPPERCASE mono** for labels, eyebrows and metrics.
No emoji — personality comes from the mascot (a blue chameleon QA companion) and
the candy accents.

## Colors

High-contrast neutrals carry the system; a single blue leads, backed by a candy
accent set used as **flat fills, never gradients**.

- **Primary `#058BFF`** — the lead blue. Logo, primary actions, links, focus.
  Darkens to **`#0070D1`** on hover/press and for blue text on light surfaces.
- **Ink `#050505`** — text, every 1px hairline stroke, illustration outlines.
  **`#6B6B6B`** for captions and muted meta.
- **Paper `#F6F2EE`** — the warm page background, softer than white. **Surface
  `#FBFBFA`** for cards and panels. **Sand `#E5DED5`** for inset fills and the
  folded-corner motif.
- **Candy accents** — Purple `#B095FA`, Pink `#FFCEE4`, Coral `#FD7876`
  (alerts), Lime `#F4FFC9` (highlights, node handles, keyword pills). Deploy
  sparingly, one accent per surface, always against the neutral paper.
- **Status** — Success `#1F8A5B` on a lime wash, alert/warning Coral, fail
  `#E5483A`.

Selection highlight is lime. Borders are ink, not gray.

## Typography

Two families, split by intent: **monospace for things that are *stated*, sans
for things that are *read*.**

- **Geist Mono** is the display/voice face — display, headings, eyebrows, CTAs,
  labels, metrics, code. It carries the technical personality.
- **Figtree** is the body face — paragraphs and UI prose, chosen for legibility
  at small sizes.
- Uppercase mono labels carry positive tracking (~`0.04em`); large headings pull
  tight (`-0.02em` to `-0.025em`). Headlines run on a snug `1.05–1.15`
  line-height; body sits at `1.5`.

Fonts load from Google Fonts (Geist Mono + Figtree); swap for self-hosted
`@font-face` if needed.

## Layout

A 4px spacing base (`xs 4 → 3xl 64`). Content maxes around 1200px with a 24px
gutter. Compositions are calm and left-aligned, with one confident focal element
per view rather than dense grids.

Recurring graphic devices act as structure, not just decoration: **window
chrome** (min/close/max dots), **folders and file/document shapes**, connector
**nodes** with lime square handles, small colored **dots**, and inline
**keyword highlight** pills. A signature `28px` **dog-ear / folded corner**
(often tinted blue, lime, coral or sand) marks cards, covers and section frames.

## Elevation & Depth

**Depth is almost flat.** When emphasis is needed, use a **hard offset "sticker"
shadow** — `3px 3px 0 #050505` (or `5px 5px 0` for larger surfaces), **no
blur**. On press, the element nudges down-right into its shadow so the offset
collapses (translate 3px, 3px). Soft blurred shadows are reserved for rare
floating UI; the default is outline + offset, never a glow.

## Shapes

Generous, consistent rounding: cards `24–32px`, inputs and buttons `8–12px`,
chips and badges fully pill. Small handles and inset chips use `4px`. Every
container carries a **1px ink hairline border**; a 2px ink border is the
strong/focus variant. Avoid borderless cards — the outline *is* the look.

## Components

All primitives share the ink hairline, the rounding scale, and mono labels.

- **button-primary** — solid blue, white mono label, ink hairline, sticker
  shadow. Hover darkens to `primary-ink`; press collapses the offset.
- **button-secondary** — surface fill, ink text and border; same shape.
- **button-ghost** — transparent, muted ink text; hover fills with sand.
- **input** — white field, ink hairline, `46px` tall; focus adds the sticker
  shadow rather than a colored ring.
- **card** — surface fill, ink hairline, `24px` radius; add the dog-ear fold for
  the brand moment.
- **badge / tag** — pill, mono uppercase label. Success rides a lime wash;
  alerts use coral.
- **keyword** — inline lime pill with ink hairline in mono, to spotlight a term
  in running text.
- **node-handle** — `26px` lime square with ink border and a mono index;
  the building block of step rails and connector diagrams.

WCAG note: white on primary blue (`#058BFF`) lands near `3.9:1` — fine for the
large mono labels on buttons (AA large ≥ 3:1), but do not set small body copy in
white on blue.

## Do's and Don'ts

- **Do** draw on warm paper with ink hairlines; keep depth flat.
- **Do** use one candy accent per surface, as a flat fill.
- **Do** reach for the folder, window-chrome, node and dog-ear motifs to add
  personality.
- **Do** set labels, eyebrows and CTAs in UPPERCASE Geist Mono; body in Figtree.
- **Don't** use gradients, soft glows, or blurred drop shadows as the default.
- **Don't** introduce new hues outside the palette, or tint imagery cool — keep
  it bright and warm to match the paper.
- **Don't** use emoji as iconography; use thin ink outline glyphs (Lucide is the
  approved stand-in until an official set ships).
- **Don't** crowd a view — one focal element, confident negative space.
