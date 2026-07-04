---
name: website-design-extractor
description: >
  Extract the full design DNA of any website — layout, color scheme, typography,
  animations, and characteristic elements — into a fixed-schema Markdown design
  spec using Claude in Chrome, captured across desktop and mobile views. Use this
  skill whenever the user provides a URL and wants its design extracted, cataloged,
  analyzed, or used as a reference for a new build. Activates on "extract this
  site's design", "website-design-extractor", "catalog this site", "I want a site
  like {URL}", "pull the design from {URL}", or any request to document how a
  website looks and behaves.
---

# Website Design Extractor

Turn any live website into a reusable design spec. The output is a self-contained,
text-only Markdown file following an identical schema every time, so specs are
mixable ("fonts from site A, hero layout from site B"), diffable, and searchable
as a catalog. Fidelity target is **pattern library, not clone**: capture concrete
values (hex codes, font families, spacing patterns, animation timing) without
attempting pixel-perfect reproduction.

## When to Activate

**Manual triggers:**
- "Extract the design from {URL}"
- "website-design-extractor {URL}"
- "Catalog this site"
- "Add {URL} to the design catalog"

**Auto-detect triggers:**
- A client wants their site "similar to" or "inspired by" another URL
- The user shares a URL and asks about its layout, fonts, colors, or animations
  in the context of building something

## Requirements

- **Claude in Chrome** must be available. This skill drives a real browser to
  view the site at multiple viewport sizes and observe live behavior. If Claude
  in Chrome is not available in the current session, stop and tell the user —
  do not attempt extraction from training knowledge or a plain fetch, as that
  cannot capture animations, responsive behavior, or rendered layout.

## Input

| Parameter | Required | Description |
|---|---|---|
| `url` | Yes | The page to extract. One URL = one spec. |
| `extra_pages` | No | Additional URLs on the same site to include in the same spec (e.g., a pricing page with a distinctive table design). |
| `review` | No | If set, run the standards review (see Review Flow) immediately after extraction. |
| `output_dir` | No | One-time override of the configured save location for this run only. |

## First-Run Configuration (save location)

The spec is saved **to the local machine only** — never to a remote repo, cloud
drive, or the conversation as the sole copy.

1. Check for the config file at `~/.config/summit/website-design-extractor.json`.
2. **If it does not exist (first run):** before extracting anything, ask the user:
   *"Where on your local machine should design specs be saved? (e.g.,
   `~/Documents/design-catalog`)"* Then create the directory if needed and write
   the config:

```json
   { "output_dir": "/absolute/path/the/user/chose" }
```

3. **If it exists:** use the stored `output_dir` without asking. Honor a per-run
   `output_dir` override without modifying the config.
4. If the user ever says "change where specs are saved", update the config file.

## Process

### Phase 1 — Desktop pass (~1440px viewport)

1. Open the URL in Claude in Chrome at a desktop viewport (~1440px wide).
2. Let the page fully load, including deferred animations. Scroll the full page
   top to bottom slowly enough to trigger scroll-based animations and lazy content.
3. Capture:
   - **Colors:** background, text, accent, and semantic colors as hex values.
     Read computed styles / CSS custom properties where accessible; otherwise
     sample visually and state values as approximate (`~#1A1A2E`).
   - **Typography:** font families (actual loaded fonts, not just CSS fallback
     stacks), weights in use, the heading scale (h1 → body relative sizing),
     line-height character (tight/airy), letter-spacing quirks.
   - **Layout & grid:** container max-width, column structure, section rhythm
     (vertical spacing pattern), header/nav pattern, footer structure, use of
     whitespace, alignment habits.
   - **Components:** buttons (shape, fill style, hover state), cards, nav,
     forms, imagery treatment (photography vs. illustration, border radius,
     shadows), iconography style.
   - **Animations & interactions:** for each observed animation, record
     *element → trigger → behavior → timing/easing*. Read duration and easing
     from computed styles or inline CSS when accessible; otherwise estimate
     ("~300ms, ease-out feel") and mark as estimated. Do NOT dump full keyframe
     code — describe behavior with timing parameters.
   - **Characteristic elements:** the 3–7 things that make this site *this
     site* — the signature moves someone would name when saying "I want it to
     feel like that."

### Phase 2 — Mobile pass (~390px viewport)

4. Reload the same URL at a mobile viewport (~390px wide) using Chrome device
   emulation. Repeat the scroll-through.
5. Capture what *changes*: nav collapse pattern (hamburger, bottom bar, etc.),
   stacking order, typography scaling, hidden/replaced elements, touch-specific
   interactions, and any animations that are disabled or simplified on mobile.

### Phase 3 — Tablet pass (~768px, conditional)

6. Briefly check the page at ~768px. **Only if** the tablet layout meaningfully
   differs from both desktop and mobile (its own grid, its own nav pattern),
   document it in the Responsive Behavior section. If it's just an intermediate
   squeeze, note "tablet: interpolates between desktop and mobile, no distinct
   layout" and move on.

### Phase 4 — Extra pages (if provided)

7. For each `extra_pages` URL, do an abbreviated desktop + mobile pass focused
   on what that page adds that the primary URL didn't show. Append findings to
   the relevant schema sections tagged with the page path.

### Phase 5 — Write the spec

8. Derive the filename: strip protocol and `www.`, replace dots with hyphens,
   append `-design-spec.md`. `https://www.stripe.com` → `stripe-com-design-spec.md`.
9. Write the spec to the configured `output_dir` using the **exact schema below**
   — same sections, same order, every time. If a section has nothing notable,
   keep the heading and write "Nothing distinctive — standard conventions."
   Never omit or reorder sections; catalog consistency depends on it.
10. Confirm the saved path to the user.

## Output Schema (fixed — never deviate)

```markdown
# Design Spec: {domain}

## Meta
- **URL:** {url} (+ extra pages if any)
- **Extracted:** {YYYY-MM-DD}
- **Viewports captured:** desktop 1440px, mobile 390px[, tablet 768px]
- **Site type:** {e.g., SaaS marketing, portfolio, e-commerce}
- **One-line character:** {e.g., "Dark, editorial, motion-heavy fintech"}

## Color Palette
| Role | Value | Notes |
|---|---|---|
| Background (primary) | #... | |
| Background (secondary) | #... | |
| Text (primary) | #... | |
| Text (muted) | #... | |
| Accent / brand | #... | |
| ... | | |
- **Palette character:** {1–2 sentences: how color is used}

## Typography
- **Display / headings:** {family, weights, where loaded from if known}
- **Body:** {family, weight}
- **Scale:** {h1 ≈ Xpx → body ≈ Ypx desktop; mobile equivalents}
- **Character:** {line-height, letter-spacing, casing habits}

## Layout & Grid
- **Container:** {max-width, gutter behavior}
- **Grid:** {column pattern}
- **Section rhythm:** {vertical spacing pattern}
- **Header/nav:** {structure, sticky behavior}
- **Footer:** {structure}
- **Whitespace & alignment:** {habits}

## Components
- **Buttons:** {shape, fill, hover, sizing}
- **Cards:** {...}
- **Forms/inputs:** {...}
- **Imagery treatment:** {...}
- **Iconography:** {...}
- {other notable components}

## Animations & Interactions
| Element | Trigger | Behavior | Timing/Easing | Measured or Estimated |
|---|---|---|---|---|
| ... | scroll / hover / load / click | ... | ~300ms ease-out | estimated |

## Responsive Behavior
- **Mobile (390px):** {nav pattern, stacking, type scaling, what's hidden/changed}
- **Tablet (768px):** {distinct layout OR "interpolates, no distinct layout"}
- **Animation changes on mobile:** {...}

## Characteristic Elements
1. {Signature move #1}
2. {...}
(3–7 items — the essence someone is asking for when they say "like this site")

## Review & Changelog
- **Standards review:** {not run | run on YYYY-MM-DD — summary}
- **Patches applied:** {none | list: what changed, why, original source value}
```

## Review Flow

- If `review` was **not** requested: after saving the spec, **always offer it**:
  *"Want me to review this spec against basic modern web standards (a11y/contrast,
  responsive integrity, semantic structure, UX conventions)?"*
- The review covers exactly: **accessibility basics** (contrast ratios of the
  captured palette pairs, focus/tap-target red flags), **responsive integrity**
  (broken or awkward mobile behavior observed), **semantic structure** (heading
  hierarchy, nav landmarks as observable), and **modern UX conventions**
  (dated patterns worth not carrying into a new build). It does **not** cover
  performance or SEO.
- Present findings as a short list, each tagged with the spec section it affects.
- **After any review, offer to patch.** Accepted patches are applied directly
  to the spec's values (e.g., bump a failing muted-text color to a compliant
  shade), and every patch is logged in **Review & Changelog** with the original
  source value preserved — the catalog must always show where the spec diverges
  from the real site.

## Rules

1. Never extract without a live browser view. No Claude in Chrome → no extraction.
2. The spec is saved locally only. Never commit specs to a repo or upload them
   anywhere unless the user explicitly asks in that session.
3. First run must configure `output_dir` before any extraction begins.
4. The schema is immutable: all sections, in order, every time.
5. Mark every value as measured or estimated — never present a visual estimate
   as a computed value.
6. Distinguish observation from inference. If an animation can't be triggered
   (login walls, hover-only on touch, etc.), say what couldn't be verified.
7. Pattern-library fidelity: capture concrete values, skip exhaustive per-element
   detail and full keyframe/source dumps.
8. Patches only ever touch the spec file — never suggest the source site is
   yours to fix.
9. If `review` was not requested, the offer to review is mandatory, once, after
   saving. After a review, the offer to patch is mandatory, once.

## Examples

**Good animation entry:**
| Hero headline | page load | fades up 20px with stagger per line | 600ms, cubic-bezier ease-out (measured) | measured |

**Bad animation entry (avoid):**
"The site has nice smooth animations throughout." — no element, trigger, or timing; unusable in a build spec.

**Good characteristic element:**
"Oversized numbered section markers (01–05) in ghosted accent color behind each section heading — the site's strongest identity device."

## Chaining

- **website-design-extractor → interrogate:** extract the reference site, then
  interrogate the client brief to decide which captured patterns apply.
- **website-design-extractor → prompt-architect / architect-plan-for-dispatch:**
  specs from the catalog feed directly into build specs for new Summit projects.
- **devils-advocate:** stress-test whether a captured pattern actually serves
  the new client's goals before adopting it.
