---
name: invoke-image
description: Generate polished, brand-consistent website imagery locally with InvokeAI at zero cost. Genre presets (photographic, editorial-food, interior-architectural, flat-vector, line-icon, watercolor, isometric-3d, seamless-texture) combine with a per-client brand file. Drafts, contact-sheet review, final render, 2x upscale, SVG vectorize. Activates on "generate images for", "hero image", "make icons for", "image set for the site", "invoke-image", or any website redesign that needs new imagery.
---

# invoke-image

Local image generation through InvokeAI on this Mac. No paid APIs.

CLI: `~/.claude/skills/invoke-image/scripts/invoke.py <command>` (runs via `uv run --script`).
Run it from inside the client repo so the brand file is found.

## Before generating

1. `invoke.py status`. If the server is down, `gen` starts it (up to 120s).
2. Look for `<repo>/.claude/image-brand.json`. If the repo is a client site and it is missing, draft one with the user:

```json
{
  "client": "Client Name",
  "brand": "palette and mood words, e.g. warm cream and diner red, retro, morning light",
  "avoid": ["readable text", "logos"],
  "default_genres": ["editorial-food", "flat-vector"],
  "output_dir": "assets/generated"
}
```

A brand file may not set model, LoRAs, or license. The search for it stops at the repo root.

## Workflow

1. **Brief.** Turn the user's short ask into a `--subject` per image (rules below). Pick genres from `default_genres` or the ask. Pick `--aspect`: hero `16:9` or `21:9`, cards `4:3` or `3:2`, portrait `9:16`, icons and textures `1:1`.
2. **Draft.** `invoke.py gen --genre <g> --subject "<s>" --aspect <a> --n 4 --draft`. Each line printed is `{path, seed, seconds, model, retry}`.
3. **Review.** `montage -font /System/Library/Fonts/Helvetica.ttc -label '%t' <draft pngs> -tile 2x -geometry 512x512+8+8 sheet.png` (the font flag is required; this ImageMagick has no default font), read the sheet, drop misses (bad anatomy, leaked text, artifacts, off-brief), show the user the rest.
4. **Final.** Re-render the chosen seed: `invoke.py gen --genre <g> --subject "<same s>" --aspect <a> --seed <seed>` (no `--draft`). Same model, full steps, so the composition carries over.
5. **Upscale heroes.** `invoke.py upscale --image <final png>` writes `<name>-up-2x.png`.
6. **Vector.** `flat-vector` and `line-icon` finals auto-vectorize to `.svg` plus `-svgcheck.png`. Read the check image before handing over the SVG. `invoke.py vectorize --image <png>` does it on demand.

## Writing the subject

- SDXL models (`juggernaut-xl`, `sdxl-base`): comma-separated descriptive phrases, subject first, then setting, lighting, and lens. Example: `stack of buttermilk pancakes, melting butter, maple syrup pour, chrome diner counter, early morning`.
- FLUX.2 Klein (`flux2-klein`): full natural sentences, composition described spatially. Example: `A tall stack of buttermilk pancakes sits on the left of a chrome diner counter while syrup pours from above; morning light comes from a window on the right.` It ignores the negative prompt.
- Never put readable words in the subject; models garble text. Add text in HTML or the design tool.
- Do not repeat the genre's style words; the genre template adds them.

## Genres

`photographic`, `editorial-food`, `interior-architectural` (photo); `flat-vector`, `line-icon` (vectorized); `watercolor`; `isometric-3d`; `seamless-texture` (tileable). Use `--model` to pick another model from a genre's `allowed_models`. New genres are JSON files in `genres/`; run `invoke.py sync-presets` after adding one so it appears in the InvokeAI UI.

## Outputs

`<output_dir>/<slug>-<genre>-<seed>.png` plus a `.json` sidecar with prompt, model, seed, license, and `invoke_image_name`. Without a brand file, output goes to `./generated/`. Each client gets an InvokeAI gallery board named after `client`; use the InvokeAI canvas (`http://127.0.0.1:9090`) for hands-on inpainting fixes.

## Rules

- Never pass `--accept-version` without asking the user. A version mismatch means the graph templates may be stale.
- Never swap to a different model because one is missing or slow; report it.
- Never use a model, LoRA, or upscaler whose `commercial_ok` is not true for a client repo. The CLI refuses; do not work around it.
- Show the user drafts before spending time on finals.

## Exit codes and failures

| Code | Meaning | Action |
|---|---|---|
| 2 | Config or input error (unknown genre, bad aspect, license refusal, missing template) | Read the message; fix the input |
| 3 | InvokeAI version differs from the pinned version | Ask the user: recapture templates, or rerun with `--accept-version` |
| 4 | Server or queue error (model not installed, timeout, failed job) | Report the InvokeAI error text verbatim |

An out-of-memory job is retried once at 0.75x size; the `retry` field says so. Tell the user.

## Maintenance

- `invoke.py selftest`: one 512px render per model family.
- `invoke.py benchmark [--model NAME]`: times each model at 1024px and records `seconds_1024` in `models.json`. Models over 300s must not be genre defaults.
- Recapturing templates after an InvokeAI upgrade: generate once in the UI with sentinel values (prompt `XPOSX`, negative `XNEGX`, seed `424242`, 1152x896 for SDXL or 1184x880 for FLUX, steps `23`, CFG `5.5` or guidance `3.7`), save the `enqueue_batch` request body to `graphs/raw/<name>-batch.json`, then run `invoke.py capture --raw ... --name <name>` with the same values plus `--model-key` and `--board-id`. Every replacement count must be at least 1. Update `invokeai_version` in `models.json`.
