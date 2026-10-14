# Motion ideas

Use when the user asks "how could this site move", "give me animation ideas", or a site feels static.

## Output: a motion plan

Return a table, one row per moment, then a short build order. Ground each row in the actual page
(read the routes and sections first).

| Section | Moment | Effect | Tool | Cost | Reduced-motion fallback |
|---|---|---|---|---|---|
| Hero | Headline on load | Words rise and unblur, 0.06s stagger | React Bits `SplitText` (gsap) | +gsap | Static text |

Rules for the plan:

- **One signature moment** (usually the hero or one pinned story section). Everything else supports it.
- **2 to 4 supporting patterns** reused across sections (same ease, same distance, same stagger) so the
  site feels designed, not decorated.
- **Micro interactions on controls** (buttons, nav, forms): short, under 300ms.
- **Name the engine budget**: gsap only, gsap + motion, or + three/ogl. Fewer is better.
- Offer 2 or 3 directions when the brand is unclear (calm/editorial, bold/kinetic, playful/tactile).

## Idea menu by section

| Section | Ideas | Tool |
|---|---|---|
| Whole site | Smooth scroll with anchor offsets | Lenis |
| Whole site | Page transitions (fade/clip wipe between routes) | GSAP timeline, or View Transitions API |
| Whole site | Film grain or subtle noise overlay | React Bits `Noise` |
| Hero | Split headline reveal (chars, words or lines) | GSAP SplitText, React Bits `SplitText`/`BlurText` |
| Hero | Rotating phrase ("Lunch. Dinner. Late night.") | React Bits `RotatingText`, `TextType` |
| Hero | Ambient animated background | React Bits Backgrounds (`Aurora`, `Silk`, `Grainient`, `DarkVeil`) |
| Hero | Image scales down from full bleed into the layout on scroll | GSAP ScrollTrigger `scrub` |
| Hero | Scroll cue that fades as you leave | ScrollTrigger |
| Story / about | Pinned section, content steps through as you scroll | ScrollTrigger `pin` + timeline `scrub` |
| Story / about | Text that brightens word by word as you read | React Bits `ScrollReveal`, GSAP SplitText + scrub |
| Story / about | Horizontal scroll gallery inside vertical page | ScrollTrigger pin + x tween |
| Story / about | Parallax layers at different speeds | ScrollTrigger `scrub`, or Lenis velocity |
| Features / menu | Cards stagger in on enter | ScrollTrigger.batch, React Bits `AnimatedContent` |
| Features / menu | Cards stack and pin as you scroll | React Bits `ScrollStack` |
| Features / menu | Spotlight or tilt on hover | React Bits `SpotlightCard`, `TiltedCard` |
| Features / menu | Filter / reorder with smooth layout change | GSAP Flip |
| Stats | Numbers count up when visible | React Bits `CountUp`, GSAP snap tween |
| Logos / press | Infinite marquee, pauses on hover | React Bits `LogoLoop` |
| Logos / press | Marquee speed tied to scroll velocity | React Bits `ScrollVelocity`, Lenis `velocity` |
| Gallery | Drag/throw carousel | GSAP Draggable + Inertia, React Bits `CircularGallery` |
| Gallery | Image trail following cursor | React Bits `ImageTrail` |
| Illustration / logo | Line drawing on scroll | GSAP DrawSVG |
| Illustration / logo | Shape morph between states | GSAP MorphSVG |
| Illustration / logo | Object follows a path as you scroll | GSAP MotionPath + ScrollTrigger |
| CTA | Magnetic button | React Bits `Magnet`, GSAP quickTo |
| CTA | Border light travelling the outline | React Bits `StarBorder` |
| CTA | Spark burst on click | React Bits `ClickSpark` |
| Nav | Header hides on scroll down, shows on up | ScrollTrigger `onUpdate` direction, Lenis `direction` |
| Nav | Pill indicator slides between links | React Bits `PillNav`, GSAP Flip |
| Nav | Full-screen menu with staggered links | React Bits `StaggeredMenu`, GSAP timeline |
| Footer | Oversized wordmark that reveals as you reach the end | ScrollTrigger scrub on clip-path |
| Forms | Field focus, success check draws in | GSAP DrawSVG, React Bits Micro (`SpringCheck`) |

## Choreography defaults

- Ease: `power3.out` or `expo.out` for entrances, `power2.inOut` for scrubbed motion.
- Duration: 0.6 to 0.9s entrances, 0.15 to 0.3s micro interactions.
- Distance: 20 to 40px translate; avoid large slides on mobile.
- Stagger: 0.04 to 0.08s per char/word, 0.08 to 0.12s per card.
- Trigger: `start: 'top 80%'`, play once (`toggleActions: 'play none none none'`) for reveals.
- Scrub: `scrub: 1` (a little lag reads smoother than `true` with Lenis).

## Where to look for more

- GSAP: https://gsap.com/showcase/ (sites), https://gsap.com/demos/ (patterns with code).
- Lenis: https://www.lenis.dev/showcase (sites built on it).
- React Bits: live demos on each component page; Background Studio at https://reactbits.dev/tools.
- Use `website-design-extractor` or the browser to study a reference site's motion before copying the feel.
