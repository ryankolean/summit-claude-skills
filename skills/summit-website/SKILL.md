---
name: summit-website
description: >
  Use when setting up, building, launching or adopting a client website with the Summit website
  framework (summit-components, SUMMIT-243): new client intake, bootstrapping a client repo,
  site.config.json decisions, proposals, building from the Astro or Next template, adding motion,
  security checks, launch, building the client brand hub, or bringing an existing site (Umbo, Fly
  Trap, Meantime) into the framework. Triggers on "new client site", "set up a website", "start a
  site for", "summit new", "summit decide", "launch this site", "adopt this site", "brand hub",
  "brand guide for <client>", "send the brand to the client", "what's the next step for this site".
---

# Summit Website

Walks one site through the framework in order and calls the right skill at each step. The framework
lives in `~/code/summit-components` (public: never put client data there). Private intake lives in
`~/code/summit-intake/<client>/`. Read both repos' `AGENTS.md` before touching them, and the client
repo's `AGENTS.md` (seeded by `summit new`) before touching it.

## Commands

`summit` is not on PATH. Define a shell function over the local build (run `pnpm build` in
summit-components first if the source changed). A `$SUMMIT` string variable does not work: zsh does
not word-split it.

```bash
summit() { node "$HOME/code/summit-components/packages/cli/dist/summit.js" "$@"; }
summit --help
```

## Find where the site is

Look before running anything: `ls ~/code/summit-intake/<client>/ ~/code/summit-intake/<client>/decisions/`
and `git status --short` in every repo you will touch. Never re-run `intake` or `decide init` over
existing files; they overwrite. Read the existing `decisions/*.md` instead.

| If the site has... | Next step |
|---|---|
| Nothing yet | 1 Intake |
| Intake done, client needs brand guidelines (or brand-only engagement) | 1b Brand hub |
| Existing site with intake and `decisions/` already in summit-intake | `summit decide validate`, then 10 Adopt from "PR 1" |
| `~/code/summit-intake/<client>/site/*.json` but no client repo | 2 Bootstrap |
| Client repo, no `decisions/site.config.json` | 3 Decide |
| Decisions, no signed proposal | 4 Proposal |
| Decisions and approval, template not copied | 5 Build |
| Built, not launched | 7 Check, then 8 Launch |
| Live | 9 Monitor |
| Existing site Summit did not build in this framework | 10 Adopt |

## 1 Intake (SUMMIT-245, docs/INTAKE.md)

```bash
summit intake <existing-site-dir> --out ~/code/summit-intake/<client> --name "<Name>"
```
Writes public `site/entity.json` + `site/brand.json` (or `*.draft.json` to fill in and rename) and
private `intake-report.md`, `entity-profile.md`, `style-guide.md`. No existing site: write
`site/*.json` by hand against `packages/schemas/src/{entity,brand}.ts` in summit-components. Then `summit verify-split ~/code/summit-intake/<client>`.

## 1b Brand hub (docs/BRAND_HUB.md)

The client-facing brand deliverable. Send this, not `style-guide.md` (that stays an internal
checklist). It can ship on its own as a brand engagement, before or without a website.

1. Intake writes `~/code/summit-intake/<client>/brand-hub.draft.json`. Put logo source files
   (SVG preferred) in `assets/logos/` and list them under `logos`, with `on` set to the color role
   each logo sits on.
2. Fill `summary`, `colorUsage`, `voice` (traits with do/don't, before/after examples), `imagery`
   and `rules` from the owner's answers. Use **summit-marketing-team** role 2 (Brand Strategist) for
   voice rules when the owner has none. Empty strings render as "Pending" under a draft banner.
3. Build a review copy any time: `summit brand-hub ~/code/summit-intake/<client>`.
4. Rename to `brand-hub.json`, rebuild, and clear every `warn:` line.
5. Output: `~/code/summit-intake/<client>/out/brand-hub/index.html`, one self-contained file
   (logos and token downloads inlined). Ryan reviews it, then sends it as an attachment or hosts it
   on a private, noindex URL. Never put it or `brand-hub.json` in a site repo; `verify-split` fails.
6. When `brand.json` changes later, rebuild and bump `version` in `brand-hub.json`.

## 2 Bootstrap

```bash
summit new <repo-name> --intake ~/code/summit-intake/<client> --dry-run   # then without --dry-run
```
Public by default (`--private` to opt out). Seeds `site/`, `AGENTS.md`, CI (`verify-split`, decide
validate, preview, check gate). Does not copy a template.

## 3 Decide (SUMMIT-246, docs/DECISIONS.md)

```bash
summit decide init . --client <repo-name> --out decisions/site.config.json [--needs auth,database,serverActions,legacyRedirects]
summit decide validate decisions/site.config.json
summit decide docs decisions/site.config.json --out decisions --brand site/brand.json
```
`design-doc.md` leaves a placeholder for layout, imagery and **motion direction**. Fill it with the
**web-motion** skill: produce its motion plan (one signature moment, supporting patterns, engine
budget, reduced-motion fallbacks) and write the plan into that section. Use `frontend-design` or
`website-design-extractor` for layout and imagery direction.

Stack rule (docs/STACK_DECISION.md): Astro for content sites, Next for auth/database/server actions,
Vite only for SEO-irrelevant SPAs. Cloudflare Pages for production (GitHub Pages cannot send
headers or 301s).

## 4 Proposal (SUMMIT-247, docs/PROPOSALS.md)

```bash
summit proposal build ~/code/summit-intake/<client> --rates ~/code/summit-intake/_summit/rate-card.example.json --draft
summit proposal publish ~/code/summit-intake --dry-run
```
Only `rate-card.example.json` exists until real pricing is decided (SUMMIT-196); keep `--draft` and
never publish a proposal built from the example card.
Output in `<client>/out/` (git-ignored). Publishing needs a live `wrangler login`. Ryan approves
before anything is published or sent.

## 5 Build (SUMMIT-249, docs/TEMPLATES.md)

1. Copy `templates/astro-site` or `templates/next-site` into the client repo.
2. `node ~/code/summit-components/scripts/use-tags.mjs <client-repo>` (pins `github:` tags).
3. Replace sample content in `site/{brand,entity,home}.json` and `public/`.
4. `pnpm install && pnpm build` (Astro: `dist/`; Next: `STATIC_EXPORT=1` writes `out/`).
5. Work through `decisions/implementation-doc.md` one PR per entry. Components come from
   `registry.json`; new ones follow `docs/ADDING_A_COMPONENT.md` in summit-components.

## 6 Motion

Load **web-motion** and build the plan from the design doc. Framework constraints that override
generic motion advice:
- Components render server-side with no client JS. Motion is a progressive layer: the built HTML
  must contain the full content, visible, with no inline `opacity:0`/`visibility:hidden`. The
  checks and answer engines read built HTML.
- Astro: motion in a client island or a `<script>`; React Bits only inside React islands.
- Static and no-build sites (Umbo, Fly Trap): GSAP + Lenis from CDN, pinned with SRI (web-motion
  `lenis.md` has the hash command), no React Bits.
- Style motion colors against `--summit-*` tokens, never hard-coded brand values.

## 7 Check

`<out>` is the build output: `dist` (Astro, Vite), `out` (Next static export), or `.` (no-build
sites such as Umbo and Fly Trap, which publish the repo root).

```bash
summit check gate <out> --mode preview
bash ~/.claude/skills/site-security/scripts/scan.sh --repo . --built <out> --url <preview-url> --mode audit --profile <brochure|app>
```
Next sites add `--allow-noindex /_not-found/` to the check.
Profile: `app` if `site.config.json` needs auth, database or serverActions, or the site stores
personal data; otherwise `brochure`. Follow the **site-security** skill for triage and fixes.
`SECURITY-REPORT.md` goes to `~/code/summit-intake/<client>/`, never the public site repo.

## 8 Launch (SUMMIT-252 not built yet: do it by hand)

1. `SITE_MODE=production SITE_URL=https://<domain> pnpm build`
2. `summit check gate <out> --mode production` must pass.
3. `scan.sh ... --mode gate` must exit 0 (1 blocked, 2 could not verify).
4. If `securityHeaders` is true, ship headers from `site-security/templates/headers` (`_headers`
   for Cloudflare Pages); the framework does not generate them yet. GitHub Pages cannot send
   headers: read `templates/headers/github-pages.md`, then either move to Cloudflare Pages or record
   the gap in the security report. Ryan decides.
5. Copy `site-security/templates/github/security.yml` into the repo so every PR runs the scans.
6. DNS, host settings and the go-live switch are Ryan's.

## 9 Monitor

Weekly `scan.sh --url https://<domain> --mode monitor` (scheduled task or the `schedule:` in
`security.yml`). `summit-checks monitor` exits 2 until SUMMIT-252 ships.

## 10 Adopt an existing site (SUMMIT-253, not built yet)

```bash
# skip the first two if the intake folder already has site/ and decisions/
summit intake <site-repo-path> --out ~/code/summit-intake/<client>
summit decide init ~/code/summit-intake/<client> --client <client> --existing <site-repo-path> --out ~/code/summit-intake/<client>/decisions/site.config.json
summit check audit <site-repo-path>
bash ~/.claude/skills/site-security/scripts/scan.sh --repo <site-repo-path> --built <out> --url https://<live> --mode audit --profile brochure
```
Live URL: read the repo's `CNAME` (custom domain) before assuming a `github.io` URL. If the repo has
no `AGENTS.md`, follow its README and the global rules.
Keep the stack. Decisions stay in the intake repo until adoption. Then PR 1 "adopt in place" per
`implementation-doc.md`.

## Rules

- summit-components: branch + PR, changeset per package change, never commit to main.
- Client repos: follow their `AGENTS.md`; one PR per implementation-doc entry.
- Nothing from `summit-intake` reaches a public repo except `site/*.json`; run `verify-split`.
- The brand hub is the brand deliverable clients receive; never send `style-guide.md` or other intake docs.
- Verify each UI step at 375 / 768 / 1280 with no horizontal overflow at 375.
