# invoke-image: local multi-style image generation skill

- Date: 2026-10-14
- Status: design approved in chat, pending written-spec review
- Sub-project 1 of 5 in the OSS-tools-as-skills effort (queue: invoke-image, Penpot, Documenso, listmonk, voicebox)

## Goal

Give Claude a skill that produces polished, brand-consistent images for client website redesigns, at zero marginal cost, on this machine. Claude's built-in image output is not polished enough for client sites.

## Constraints

- **Zero cost.** No paid APIs, no hosted inference. Everything runs locally.
- **Hardware.** Apple M1 Pro, 16GB unified memory, ~217GB free disk. InvokeAI states "16GB+ recommended" for Apple Silicon, so this machine is at the floor.
- **No Docker for inference.** Docker on macOS has no Metal GPU access; CPU-only diffusion is unusable.
- **Client deliverables must be commercially licensed.** Every model and LoRA carries a license field; non-commercial assets are blocked for brand-scoped work.

## Asset types in scope

Photoreal hero and lifestyle, illustrations, icons / vector / logos, textures and backgrounds. More types will follow; the genre system must accept new genres without code changes.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Engine | InvokeAI, native install via the official Launcher | Apache-2.0, maintained, SDXL + FLUX + GGUF, REST API, canvas/inpainting, native Style Presets |
| Rejected: Fooocus | Not used | SDXL only, no official API, Mac is secondary |
| Rejected: mflux | Possible second backend later | Faster FLUX on MLX, but no GUI/canvas and FLUX-only |
| Rejected: third-party `invokeai-mcp` | Not used | 1 star, single maintainer; a thin own client is safer |
| Cost model | Local only | User requirement: zero cost |
| Style model | Genre presets + per-client brand overlay | Reusable genres; brand consistency per site |
| Brand file location | In each client repo | Versioned with the site, auto-detected from cwd |
| Skill source | `skills/invoke-image/` in this repo, symlinked into `~/.claude/skills/` | Matches the career-launchpad symlink pattern |

## Section 1: runtime and models

### Runtime

- InvokeAI installed natively via the Launcher; serves `http://127.0.0.1:9090`.
- Not always-on (RAM pressure on 16GB). The skill probes `GET /api/v1/app/version`; if down, starts the headless `invokeai-web` from the install in the background, waits up to 120s, leaves it running for the session.
- One model resident at a time; InvokeAI RAM cache kept small.

### Starter models (~30GB)

| Role | Model | License for client output |
|---|---|---|
| Photoreal hero/lifestyle | Juggernaut XL (SDXL fine-tune) | Verify at install time; record in `models.json` |
| Illustration, textures, flat | SDXL base + per-genre LoRAs | Per-LoRA `license`; non-commercial blocked |
| Fast drafts | FLUX.1-schnell GGUF | Apache-2.0 |
| Polished finals | FLUX.1-dev GGUF Q4 or Q8 | License section 2(d): outputs usable commercially, except to train competing models (verified 2026-10-14) |
| Upscale | InvokeAI built-in upscaler | Bundled |

### Vector

vtracer (local) converts a posterized, high-contrast raster render to SVG. Good for icons and flat marks; weak for detailed illustration, by design.

### Speed gate

The first implementation task benchmarks every model at 1024px on this machine. Any model slower than ~5 minutes per image is removed from defaults (FLUX.1-dev Q8 is the likely casualty; Q4 is the fallback). Measured seconds are written into `models.json` and replace all estimates in this spec.

## Section 2: skill layout and style system

### Layout

```
skills/invoke-image/
  SKILL.md            triggers, workflow, per-family prompt rules
  scripts/invoke.py   CLI: status | start | gen | upscale | vectorize | sync-presets | selftest
  graphs/             node-graph templates: sdxl.json, flux.json, upscale.json
  models.json         registry: InvokeAI model key, family, license, commercial_ok,
                      default steps/cfg/scheduler, benchmarked seconds, pinned InvokeAI version
  genres/*.json       genre presets
  tests/              pytest unit tests (no server)
```

`invoke.py` is a single-file Python script with uv inline dependencies (`# /// script`), so no venv.

### Graph templates

Captured, not hand-written. For each model family, generate once in the InvokeAI UI, capture the graph the UI posts to `/api/v1/queue/default/enqueue_batch`, and template it with placeholders (positive, negative, seed, width, height, steps, cfg, model key, LoRAs, board). This pins templates to known-valid graphs for the pinned InvokeAI version.

### Genre preset

Starter set of 8: `photographic`, `editorial-food`, `interior-architectural`, `flat-vector`, `line-icon`, `watercolor`, `isometric-3d`, `seamless-texture`. Templates are written fresh (Fooocus style files are GPL-3.0 and are not copied).

```json
{
  "name": "flat-vector",
  "model": "sdxl-base",
  "allowed_models": ["sdxl-base", "flux-dev"],
  "positive": "{subject}, flat vector illustration, clean shapes, limited palette, {brand}",
  "negative": "photo, gradient noise, text, watermark",
  "loras": [{"key": "...", "weight": 0.7}],
  "steps": 30,
  "cfg": 6,
  "vectorize": true
}
```

`sync-presets` upserts every genre into InvokeAI Style Presets so the same styles are usable by hand in the UI.

### Brand overlay

File: `<client-repo>/.claude/image-brand.json`, found by walking up from cwd.

```json
{
  "client": "Fly Trap",
  "brand": "warm cream and diner red, retro Ferndale, morning light",
  "avoid": ["readable text", "logos", "close-up faces"],
  "default_genres": ["editorial-food", "flat-vector"],
  "output_dir": "assets/generated"
}
```

Merge rules:

- `{brand}` in the genre positive is replaced by `brand.brand`; empty string when no brand file.
- `brand.avoid` is appended to the genre negative.
- A brand file cannot set model, LoRAs, or license. Those come only from the genre and `models.json`.
- No brand file: output goes to `./generated/`.

### Prompt expansion

Claude writes `{subject}` from a short user brief. Rules in SKILL.md:

- SDXL family: comma-separated descriptive tags, subject first, lighting and lens terms explicit.
- FLUX family: full natural-language sentences, composition described spatially.

### Output

- File: `<output_dir>/<slug>-<genre>-<seed>.png`
- Sidecar: same name `.json` with prompt, negative, model key, LoRAs, seed, steps, cfg, size, InvokeAI version, license, `commercial_ok`.
- Each client gets a gallery board in InvokeAI named after `brand.client`.

## Section 3: flow, errors, testing

### Flow

1. **Brief.** Claude picks genres (brand `default_genres` or the request), aspect, variant count (default 4).
2. **Draft.** `invoke.py gen --genre <g> --subject "<s>" --aspect 16:9 --n 4 --draft` uses FLUX.1-schnell or reduced steps. Prints one JSON line per image: `{path, seed, seconds}`.
3. **Review.** ImageMagick `montage` builds a contact sheet; Claude reads it, drops misses against the brief (anatomy, artifacts, leaked text), presents the rest.
4. **Final.** The chosen seed is re-rendered on the final model; heroes are upscaled 2x.
5. **Vector.** Genres with `vectorize: true`: posterize, vtracer to SVG, rasterize the SVG back to PNG so Claude can verify the trace.

### Error handling

No silent fallbacks.

| Failure | Behavior |
|---|---|
| Server down | Auto-start, 120s timeout, then exit non-zero with a clear message |
| Model not installed | Name it, print the install command; never substitute another model |
| `commercial_ok: false` and a brand file is present | Refuse, naming the model or LoRA and its license |
| OOM or MPS error | Retry once at lower resolution or smaller quant; the retry is stated in output and sidecar |
| Queue item failed | Surface the InvokeAI error text verbatim |
| Hung job | Cancel at 3x benchmarked seconds |
| InvokeAI version differs from pinned | Warn that graph templates need recapture; refuse to run until the user confirms |

### Testing

- **Unit (pytest, no server):** genre + brand merge; license gate; filename and sidecar contents; aspect-to-pixel math (multiples of 64 for SDXL, 16 for FLUX).
- **Smoke:** `invoke.py selftest` renders one 512px image per model family and checks PNG, sidecar, and board.
- **Benchmark:** the speed gate in section 1.
- **Acceptance:** a real image set for Fly Trap (`~/flytrap-website`), four genres under its brand file. Pass = the user judges it polished enough to ship on the live site. On fail, tune presets and LoRAs before moving to sub-project 2.

## Repo integration

Per this repo's AGENTS.md, adding the skill also requires:

1. A row in the "Summit Custom Skills" table in `README.md`.
2. A numbered entry in the install-prompt block in both `README.md` and `install-prompts/ALL-PROMPTS.md`, renumbering later entries in place.

This repo is public. No client data lands here: brand files live in client repos, generated images live in client repos.

## Delivery

All work lands via pull requests. Nothing is merged without the user's explicit approval.

## Out of scope

- Paid or hosted generation APIs.
- Model training or LoRA fine-tuning.
- mflux backend.
- Sub-projects 2 to 5 (each gets its own spec).
