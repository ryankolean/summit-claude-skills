# Lenis reference

Package `lenis` (v1.3.x). React adapter `lenis/react`, Vue `lenis/vue`, snap plugin `lenis/snap`.
Source of truth: https://github.com/darkroomengineering/lenis (README) and https://lenis.dev.

## Vanilla + GSAP ScrollTrigger

```js
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const lenis = new Lenis({ anchors: true })      // autoRaf defaults to false
lenis.on('scroll', ScrollTrigger.update)

const tick = (time) => lenis.raf(time * 1000)   // gsap time is seconds, lenis wants ms
gsap.ticker.add(tick)
gsap.ticker.lagSmoothing(0)

// teardown (SPA route change, HMR)
// gsap.ticker.remove(tick); lenis.destroy()
```

Without GSAP: `new Lenis({ autoRaf: true })` and nothing else.

## React + GSAP

```jsx
import { ReactLenis, useLenis } from 'lenis/react'
import 'lenis/dist/lenis.css'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useEffect, useRef } from 'react'

gsap.registerPlugin(ScrollTrigger)

export function SmoothScroll({ children }) {
  const lenisRef = useRef(null)

  useLenis(ScrollTrigger.update)   // `root` makes the instance reachable here

  useEffect(() => {
    const tick = (time) => lenisRef.current?.lenis?.raf(time * 1000)
    gsap.ticker.add(tick)
    gsap.ticker.lagSmoothing(0)
    return () => gsap.ticker.remove(tick)
  }, [])

  return (
    <ReactLenis root options={{ autoRaf: false, anchors: true }} ref={lenisRef}>
      {children}
    </ReactLenis>
  )
}
```

Mount once at the app root. Animations inside components use `useGSAP` (see `gsap-skills:gsap-react`).
Next.js App Router: put this in a `'use client'` component inside `layout.tsx`.

## Static / no-build site (CDN)

```html
<link rel="stylesheet" href="https://unpkg.com/lenis@1.3.26/dist/lenis.css"
  integrity="sha384-gvLq/iOMNnPchdosgVym5huSVkKipHCQaqSw2Eg0V52Mzmlf169ZOsXcNc2cNu8x" crossorigin="anonymous">
<script src="https://unpkg.com/lenis@1.3.26/dist/lenis.min.js"
  integrity="sha384-Mp//F5qKhQeMvZG7i4+TqIwIJzYacAZldPBlCi33v7YJrddKC3iQxF++H576Bt1q" crossorigin="anonymous"></script>
<script>
  new Lenis({ autoRaf: true, autoToggle: true, anchors: true, allowNestedScroll: true, stopInertiaOnNavigate: true })
</script>
```

Pin exact versions and keep `integrity` on every CDN tag. New version: recompute with
`curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A`.

With GSAP from CDN, use the vanilla pattern above with the `window.Lenis` / `window.gsap` globals
instead of `autoRaf: true`.

## Options worth knowing

| Option | Default | Use |
|---|---|---|
| `lerp` | `0.1` | Smoothness (lower = floatier). Overrides `duration`/`easing`. |
| `duration` / `easing` | `1.2` / expo-out | Time-based feel when `lerp` is unset. |
| `anchors` | `false` | `true` or `{ offset: 80 }` so `#hash` links smooth-scroll (offset for sticky headers). |
| `autoToggle` | `false` | Start/stop from wrapper `overflow` (modals with `overflow: hidden`). Needs lenis.css. |
| `allowNestedScroll` | `false` | Let nested scrollers scroll natively. DOM walk per event; prefer `data-lenis-prevent` on big pages. |
| `prevent` | - | `(node) => node.closest('.modal')` to skip smoothing per element. |
| `syncTouch` | `false` | Smooth touch too. Unstable on iOS < 16; leave off unless a WebGL scene needs it. |
| `orientation` / `gestureOrientation` | `vertical` | Horizontal scroll sections. |
| `infinite` | `false` | Looping pages (needs `syncTouch` on touch). |
| `respectReducedMotion` | `true` | Leave on. `lenis.prefersReducedMotion` tells your own code. |

## API

- `lenis.scrollTo(target, { offset, duration, immediate, lock, force, onComplete })`: target is px,
  selector, element, or `'top'`/`'bottom'`.
- `lenis.stop()` / `lenis.start()`: lock scroll for modals and menus.
- `lenis.on('scroll', ({ scroll, velocity, direction, progress }) => ...)`: velocity-driven effects
  (skew on fast scroll, marquee speed).
- `lenis.resize()`: after content height changes if `autoResize` is off.

## Nested scroll / modals

```html
<div data-lenis-prevent>scrolls natively</div>
```
Also `data-lenis-prevent-wheel`, `-touch`, `-vertical`, `-horizontal`.

## Limits

- No CSS `scroll-snap`; use `lenis/snap`.
- Safari caps at 60fps (30fps in low power mode).
- Wheel events do not cross iframes (embeds like maps, Untappd, Toast) so smoothing pauses over them.
- `position: fixed` can lag on pre-M1 macOS Safari.
