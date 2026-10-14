---
name: web-motion
description: >
  Use when building or reworking a website and adding motion: smooth scroll, scroll-triggered
  reveals, hero or text animations, animated backgrounds, cursor effects, hover and micro
  interactions, page transitions, or when asked for animation ideas. Covers GSAP (gsap.com),
  Lenis (lenis.dev) and React Bits (reactbits.dev). Triggers on "add motion", "animate this
  site", "make it feel premium", "smooth scrolling", "scroll animations", "ScrollTrigger",
  "Lenis", "React Bits", "animated background", "motion ideas".
---

# Web Motion

Three sources, three jobs. Pick the right one per effect, wire them through one animation loop,
and ship every effect with a reduced-motion fallback.

| Source | Job | Where the detail lives |
|---|---|---|
| **GSAP** (gsap.com) | Animation engine: tweens, timelines, ScrollTrigger, SplitText, Flip, DrawSVG, MorphSVG. 100% free incl. all plugins, commercial OK. | Official plugin skills: `gsap-skills:gsap-core`, `gsap-react`, `gsap-scrolltrigger`, `gsap-timeline`, `gsap-plugins`, `gsap-performance`, `gsap-frameworks`, `gsap-utils`. Load the one that fits. |
| **Lenis** (lenis.dev) | Smooth scroll on top of native scroll. Feeds ScrollTrigger. | [lenis.md](lenis.md) |
| **React Bits** (reactbits.dev) | 200+ copy-in React components: text animations, animations, UI components, micro interactions, backgrounds. Source lands in the repo, not node_modules. | [react-bits.md](react-bits.md) |

Any request for ideas, a motion plan, or "what should move": use [motion-ideas.md](motion-ideas.md)
and return its plan table (includes cost and reduced-motion fallback per row).

## Live sources (catalogs change weekly; check before naming a component or API)

```bash
curl -sL https://reactbits.dev/llms.txt   # full free catalog with CLI names
curl -sL https://gsap.com/llms.txt        # GSAP docs index
curl -sL https://raw.githubusercontent.com/darkroomengineering/lenis/main/README.md
```

Inspiration: https://gsap.com/showcase/, https://gsap.com/demos/, https://www.lenis.dev/showcase,
reactbits.dev category pages (live previews with prop controls).

## Stack decision

- **React / Next / Vite+React / Astro with React islands:** all three. React Bits for drop-in pieces,
  GSAP via `useGSAP` for custom choreography, Lenis via `lenis/react`.
- **Static HTML or no-build site:** GSAP + Lenis from CDN. React Bits does not apply; rebuild the
  effect with GSAP using the React Bits source as a reference. Vue and Svelte have official ports
  (vue-bits.dev, sveltebits.xyz).
- **Smooth scroll:** Lenis or GSAP ScrollSmoother, never both.

## Integration rules

1. **One loop.** When GSAP is present, drive Lenis from `gsap.ticker` with `autoRaf: false` and
   `gsap.ticker.lagSmoothing(0)`. Never also set `autoRaf: true` (double-steps the scroll).
2. **Sync ScrollTrigger:** `lenis.on('scroll', ScrollTrigger.update)` (React: `useLenis(ScrollTrigger.update)`).
3. **Cleanup removes the same function reference you added.** `gsap.ticker.remove(lenis.raf)` does
   nothing if you added an arrow wrapper; store the wrapper. React StrictMode mounts twice, so a
   leaked ticker callback means two loops.
4. **Import `lenis/dist/lenis.css`** and do not set `scroll-behavior: smooth` on `html`.
5. **React Bits installs need the variant suffix:** `https://reactbits.dev/r/<Name>-<JS|TS>-<CSS|TW>`.
   A bare `/r/TextType` 404s.
6. **Check React Bits dependencies first** (gsap, motion, three, ogl, matter-js...). Two motion
   engines (GSAP + Motion) in one bundle is a cost; prefer components that share the engine you
   already ship.
7. **Reduced motion:** Lenis honors `prefers-reduced-motion` by default. Wrap GSAP work in
   `gsap.matchMedia()` with `(prefers-reduced-motion: no-preference)`. React Bits components mostly
   do not check it: gate them yourself and render a static fallback.
8. **Content is visible without JS.** Reveals animate `opacity`/`transform` from a state set by JS
   (`gsap.from`, `autoAlpha`), never from CSS that hides content before JS runs.
9. **Performance budget:** one WebGL background per page, paused offscreen, static image fallback on
   mobile or low-power. Animate transform/opacity only. Use `fixing-motion-performance` for jank.

## Verify

- Build passes; console has no errors at 375 / 768 / 1280.
- Scroll the whole page: ScrollTrigger markers line up with Lenis on (`markers: true` while testing).
- Emulate `prefers-reduced-motion: reduce` (DevTools Rendering panel, or Playwright
  `reducedMotion: 'reduce'`): no smoothing, no entrance motion, all content visible.
- Anchor links and keyboard scroll (Space, PageDown, Tab) still work; modals and nested scrollers
  scroll (`data-lenis-prevent`).
- Hidden preview tabs stall `requestAnimationFrame` and IntersectionObserver; take a screenshot to
  force frames before judging an animation broken.

## Common mistakes

| Mistake | Fix |
|---|---|
| `npx shadcn add https://reactbits.dev/r/Aurora` | Add the variant: `Aurora-TS-TW` |
| `shadcn add` in a repo with no `components.json` | `npx shadcn@latest init` first, or use jsrepo, or copy source manually |
| Lenis + ScrollSmoother together | Pick one |
| `@studio-freight/lenis` or `@studio-freight/react-lenis` | Renamed: `lenis` and `lenis/react` |
| Telling the user GSAP plugins need Club GreenSock | All plugins are free since 3.13 (`npm i gsap`) |
| Effect on every section | One signature moment, a few supporting reveals, micro interactions on controls |
