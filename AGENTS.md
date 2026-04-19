# AGENTS.md — summit-claude-skills

Agent-facing guide for the Summit Claude Skills repo. Human-facing docs live in [`README.md`](./README.md).

## Project overview

A curated directory of third-party Claude skills, MCP servers, and prompt libraries, plus a growing set of Summit-authored custom skills under `skills/`. The repo is mostly documentation (the README is the primary artifact) with skill definitions as standalone `SKILL.md` files organized one per directory.

## Tech stack

- Markdown (README is the directory; each custom skill is its own `SKILL.md`)
- Shell scripts in `scripts/` (`.sh`)
- Static assets in `assets/`
- Install-prompt text in `install-prompts/ALL-PROMPTS.md`

## Commands

No build or test pipeline. Useful scripts:

- `scripts/check-broken-links.sh` — validate external links in README
- `scripts/update-stars.sh` — refresh GitHub star counts (if present)

Run ad hoc from the repo root.

## Structure

- `README.md` — top-level directory; source of truth for the curated list and custom-skills table
- `CONTRIBUTING.md` — submission rules for third-party entries
- `skills/{skill-name}/SKILL.md` — one directory per Summit-authored skill
- `install-prompts/ALL-PROMPTS.md` — canonical install-prompt block mirrored in README
- `templates/` — reusable starter files (personal CLAUDE.md template, etc.) — not skills; copy-and-fill
- `assets/` — logos and static images
- `scripts/` — maintenance shell scripts

## Conventions

- **One skill per directory** under `skills/`. Every skill ships a `SKILL.md` with frontmatter (`name`, `description`, `when_to_use` / triggers) followed by rules and examples.
- **Two places to update when adding a Summit skill:**
  1. A new row in the "Summit Custom Skills" table in `README.md`
  2. A numbered entry in the install-prompt block (both in `README.md` and `install-prompts/ALL-PROMPTS.md`)
  Renumber later entries (e.g., MENTOR SKILLS, MENTOR COUNCIL) to keep ordering consistent.
- **No emojis** anywhere — README, SKILL.md, commit messages, or install prompts.
- **Commit messages:** conventional style (`feat:`, `fix:`, `docs:`, `chore:`), short imperative first line.
- **Direct commits to `main`** — no feature branches, no PRs, unless the change is risky or collaborative.
- **External entries** must meet the bar in `CONTRIBUTING.md` (100+ stars, active maintenance, OSS license).
- **Third-party skills are never redistributed** — we only link. Do not copy a skill's source into this repo.

## Do not

- Do not add emojis to the README or any SKILL.md
- Do not rewrite the install-prompt block from scratch — it's numbered and ordered; insert/renumber in place
- Do not create a skill directory without also updating the README table and install-prompt list
- Do not commit `node_modules/`, local caches, or editor state
- Do not redistribute third-party skill source code — link to the origin repo instead

## Related repos

- [`ryankolean/mindspace`](https://github.com/ryankolean/mindspace) — driven by the `brain-dump` skill here
- [`ryankolean/estatesync`](https://github.com/ryankolean/estatesync) — primary consumer of several Summit skills
