# Stage 5 — Motion graphics via HyperFrames

Author HTML/CSS/GSAP compositions, render to transparent-background MP4 overlays.

## Tool
`npx hyperframes` from `heygen-com/hyperframes`. Renders an HTML page through a paused GSAP timeline + headless Chromium, frame by frame.

## When to use
- Lower-thirds (name + title cards).
- Animated text emphasis (kinetic typography).
- Logo stings / outro cards.
- Data viz overlays (numbers, charts, progress bars).
- Section dividers / chapter cards.

For 2D math/diagram animation, use Manim via the `browser-use/video-use` skill instead — it's better at parametric geometry.

## File layout

```
compositions/
  lower-third-name/
    index.html
    style.css
    timeline.js   # paused GSAP timeline
    config.json   # {duration:3.0, fps:30, w:1080, h:1920, transparent:true}
  callout-stat/
    ...
```

## Composition skeleton

`index.html`:
```html
<!doctype html>
<html><head><link rel="stylesheet" href="style.css"></head>
<body>
  <div class="lt">
    <div class="lt__name">Ryan Kolean</div>
    <div class="lt__title">Summit Software Solutions</div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script src="timeline.js"></script>
</body></html>
```

`timeline.js`:
```js
const tl = gsap.timeline({paused: true});
tl.from(".lt__name",  {y: 40, opacity: 0, duration: 0.6, ease: "power3.out"})
  .from(".lt__title", {y: 20, opacity: 0, duration: 0.4, ease: "power2.out"}, "-=0.3")
  .to(".lt", {opacity: 0, duration: 0.4}, ">+1.5");
window.__hyperframesTimeline = tl;   // hyperframes scrubs this
```

## Render

```bash
npx hyperframes render \
  --input compositions/lower-third-name \
  --output compositions/out/lower-third-name.mov \
  --transparent
```
Output: ProRes 4444 or VP9 alpha — transparent background preserved for stage 7 overlay.

## Output
`compositions/out/*.mov` per overlay, plus an `overlays.json` describing where each one sits on the timeline:
```json
{
  "overlays": [
    {"file": "lower-third-name.mov", "start": 1.5, "anchor": "bottom-left", "x": 80, "y": 120}
  ]
}
```

## Pitfalls
- Forgetting `window.__hyperframesTimeline = tl` → hyperframes can't find the scrub handle, exports a static frame.
- Using CSS `animation` instead of GSAP — hyperframes can't pause keyframe animations deterministically.
- Web fonts that load async — fonts may not be ready at frame 0. Preload with `<link rel="preload" as="font" crossorigin>` and gate timeline start on `document.fonts.ready`.
- Large background images crater render time. Inline SVG > raster.
