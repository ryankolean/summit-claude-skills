# React Bits reference

Free, MIT + Commons Clause, by David Haz. 200+ components in five groups: Text Animations, Animations,
Components, Micro, Backgrounds. Each ships in 4 variants: JS-CSS, JS-TW, TS-CSS, TS-TW. Code is copied
into the repo (you own and edit it). Vue port: vue-bits.dev. Svelte port: sveltebits.xyz.

## Find a component

```bash
curl -sL https://reactbits.dev/llms.txt | grep -i 'scroll'          # search the live catalog
curl -sL https://reactbits.dev/llms.txt | sed -n '/^## Backgrounds/,/^## Variants/p'
```

Catalog line format: `- [Blur Text](https://www.reactbits.dev/text-animations/blur-text): ... CLI: \`BlurText\``.
Page URL is kebab-case (live demo + prop controls), CLI name is PascalCase. Do not guess names: if it is
not in llms.txt it does not exist in the free library.

## Check dependencies before installing

```bash
curl -sL https://reactbits.dev/r/BlurText-TS-TW.json | jq '.dependencies'
# ["motion@^12.23.12"]
```

Engines in use across the library: `gsap`, `motion` (Framer Motion), `three`, `ogl`, `matter-js`, or none
(plain canvas/WebGL/CSS). Prefer components on the engine the site already ships.

## Install

Pick the variant matching the repo: TS or JS, Tailwind (`TW`) or plain CSS (`CSS`).

```bash
npx shadcn@latest add https://reactbits.dev/r/BlurText-TS-TW
npx jsrepo@latest add https://reactbits.dev/r/BlurText-TS-TW
```

- shadcn needs `components.json` (run `npx shadcn@latest init` first in a non-shadcn repo). It installs npm
  deps and writes the file under the configured components path.
- jsrepo does not use `components.json`; on first run it may ask where to write files. Answer with the
  repo's components folder (e.g. `src/components`) and confirm deps landed in `package.json` afterward.
- Namespaced form, after adding `"registries": { "@react-bits": "https://reactbits.dev/r/{name}.json" }`
  to `components.json`: `npx shadcn@latest add @react-bits/BlurText-TS-TW`.
- No CLI: open the component page, choose the variant, copy source, install listed deps.
- MCP: React Bits works through the shadcn MCP server once the registry is in `components.json`
  (`npx shadcn@latest mcp init --client claude`, per project).
- React Bits Pro (`@reactbits-starter/...`) is a paid, license-keyed registry. Only mention it when the
  user wants full page blocks, app UI or templates; never run its install without a license.

## After install

- Read the copied source. Props are documented at the top and on the demo page.
- Add a `prefers-reduced-motion` gate (most components do not check it).
- Canvas/WebGL backgrounds: set an explicit height on the parent, `pointer-events: none` if decorative,
  `aria-hidden="true"`, and stop the loop when offscreen.
- Text animations that split text: keep the real string available to screen readers (`aria-label` on
  the wrapper, split spans `aria-hidden`).

## Picks by job (deps verified 2026-10; re-check with the JSON above)

| Job | Components | Deps |
|---|---|---|
| Hero headline entrance | `SplitText`, `BlurText`, `TextType`, `RotatingText`, `Shuffle`, `DecryptedText` | SplitText: gsap, BlurText: motion |
| Headline accent | `GradientText`, `ShinyText`, `MaskedHeading`, `StrokeText` | Gradient/Shiny: none |
| Scroll-linked text | `ScrollReveal`, `ScrollFloat`, `ScrollVelocity` | ScrollReveal: gsap |
| Section entrance wrapper | `AnimatedContent`, `FadeContent`, `GradualBlur` | AnimatedContent: gsap |
| Stats / numbers | `CountUp`, `Counter` | CountUp: motion |
| Logo / press strip | `LogoLoop` | none |
| Feature cards | `SpotlightCard`, `MagicBento`, `TiltedCard`, `BorderGlow`, `GlareHover`, `ChromaGrid` | Spotlight: none, Tilted: motion |
| Stacked / scroll story | `ScrollStack`, `ScrollExpand`, `CardSwap`, `FlyingPosters` | ScrollStack: none |
| Galleries | `CircularGallery`, `DomeGallery`, `Masonry`, `Carousel`, `AccordionGallery` | check |
| Navigation | `PillNav`, `CardNav`, `StaggeredMenu`, `GooeyNav`, `FlowingMenu`, `BubbleMenu` | check |
| Buttons / CTAs | `Magnet`, `StarBorder`, `ClickSpark`, `SpecularButton`, `HoldButton` | Magnet, ClickSpark: none |
| Soft ambient background | `Aurora`, `SoftAurora`, `Silk`, `Grainient`, `DarkVeil`, `Iridescence` | Aurora, Silk: none |
| Techy / grid background | `DotGrid`, `RippleGrid`, `GridScan`, `Threads`, `Waves`, `FloatingLines` | DotGrid, Threads: none |
| Dramatic background | `Galaxy`, `Hyperspeed`, `LightRays`, `Beams`, `Particles`, `Ballpit` | Ballpit: gsap + three |
| Texture overlay | `Noise` | none |
| Cursor flourish | `SplashCursor`, `BlobCursor`, `TargetCursor`, `ImageTrail` | check; desktop only |
| Playful | `FallingText`, `StickerPeel`, `Lanyard` | FallingText: matter-js |

Free tools at https://reactbits.dev/tools: Background Studio (tune and export backgrounds as code,
image or video), Shape Magic (inner-rounded shapes to SVG/clip-path), Texture Lab (noise, dither,
ASCII effects on images/video).
