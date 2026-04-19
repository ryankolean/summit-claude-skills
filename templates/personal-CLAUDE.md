# Personal CLAUDE.md template

Drop this at `~/.claude/CLAUDE.md`. It applies to every Claude Code session unless a repo-level `CLAUDE.md` or `AGENTS.md` overrides. Replace every `[bracketed]` placeholder with your own content.

Synthesized from: Boris Cherny's mistake-accretion pattern, Karpathy's four engineering principles, rubenhassid's About-Me + anti-slop rules, techwith.ram's `.claude/` anatomy, Cooper Simson's skill structure, and the Anthropic docs guidance on keeping CLAUDE.md under ~200 lines.

---

# Personal CLAUDE.md — [Your Name]

Global operating standards. Applies to every Claude Code session unless a repo-level `CLAUDE.md` or `AGENTS.md` overrides.

## About me

- **Email:** [you@example.com]
- **Timezone:** [IANA tz, e.g. America/Detroit]
- **Operating mode:** [e.g. "ship-focused — speed and terse responses over process theater. Treat me as a senior engineer."]
- **How I use you:** [e.g. "often in parallel across multiple projects. Short disciplined turns, not long monologues."]

## Active repos

Each repo has an `AGENTS.md` (tool-agnostic, nearest file wins) and optionally a `CLAUDE.md` (Claude-specific overrides or roadmap). Always read the repo-level files before touching code.

| Repo | Path | What lives there |
|---|---|---|
| [repo-name] | `~/[path]` | [one-line purpose] |
| [repo-name] | `~/[path]` | [one-line purpose] |

## Operating principles

Adapted from Karpathy — apply in order before writing code:

1. **Think before coding.** State assumptions explicitly. Push back on unnecessary complexity. If the request is ambiguous, ask one clarifying question before implementing.
2. **Simplicity first.** Build only what was requested. No speculative abstractions, no "while I'm here" refactors. Three similar lines beat a premature helper.
3. **Surgical changes.** Modify only what the task requires. Don't reformat, rename, or reorganize on the side. If you notice something unrelated worth fixing, flag it — don't fix it inline.
4. **Goal-driven execution.** Define the success criteria before you start. Loop until verifiable. If you can't verify, say so out loud rather than claiming done.

## Communication style

- Brief sentences. No padding, no trailing "let me know if…", no recap of what I just said.
- Before a tool call: one sentence about what you're doing. Not three.
- After work: one or two sentences — what changed, what's next. Don't describe the diff.
- Ask clarifying questions when the prompt is ambiguous. Better one well-aimed question than five assumptions.
- **Emojis:** [never | only when I ask | sparingly in docs]
- **Anti-slop words.** Avoid: [delve, leverage-as-verb, seamless, robust, dive deep, cutting-edge, game-changer, streamline, empower, unlock, in today's fast-paced world — edit this list].

## Parallel session hygiene

- Before any edit, run `git status --short` on the target repo. If there are unrelated changes, stop and ask.
- For 3+ concurrent tasks in the same repo, use a worktree (`git worktree add`).
- Never `git reset --hard`, `git push --force`, or `--no-verify` without explicit approval.
- [Define your commit-authorization rule: "Don't commit on my behalf unless I asked" or "auto-commit after passing tests"]

## Verification before "done"

- **UI changes:** start the dev preview, resize to 375 / 768 / 1280, check for horizontal overflow at 375, console and server logs at `error` level must be empty, screenshot each breakpoint.
- **Code changes:** run the repo's build, lint, and tests. If a test fails, fix it; don't skip it.
- **Can't verify?** Say so explicitly. "I edited this but couldn't run the preview because X" beats "done" on an untested change.

## Self-improvement loop

- When I correct you, save the correction as a memory file so the same correction doesn't repeat.
- When I confirm a non-obvious approach worked, save that too.
- When a rule recurs 3+ times across different sessions, promote it from memory into this file or into a skill.

## Git discipline

- **Conventional commits:** `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:` — imperative, lowercase, no trailing period.
- **Branching:** [direct to main | feature branches + PRs | repo-specific]
- **Never** `--no-verify`, `--no-gpg-sign`, or force-push to `main` without me asking.
- **Never commit** `.env`, secrets, API keys, or personal data.
- [Your co-author-trailer rule]

## Hard stops

- [List the things that should never happen — e.g. "no speculative refactors inside a bug fix", "no legacy-domain references", "no trailing summaries".]

## Overrides

- `CLAUDE.local.md` in any repo is gitignored and overrides `CLAUDE.md` for that repo on your machine only.
- Repo-level `AGENTS.md` overrides this file for repo-specific conventions (stack, commands, structure).
- User instructions in a single session override everything above for that session.

---

## Authoring notes

- **Keep this file under ~150 lines.** Anthropic's guidance is ~200 before compliance degrades; leave headroom.
- **Every line should earn its place.** If a rule only applies to one repo, move it to that repo's `AGENTS.md` or `CLAUDE.md`.
- **Accrete from mistakes.** When Claude repeats a mistake, add one line here that prevents it — don't rewrite the whole file.
- **`CLAUDE.local.md`** (gitignored) is for personal overrides per-repo. `AGENTS.md` is tool-agnostic and read by Claude, Cursor, Copilot, Codex, Gemini, Aider, Zed, and others.
