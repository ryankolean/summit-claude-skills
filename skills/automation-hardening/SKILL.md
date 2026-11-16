---
name: automation-hardening
description: >
  Audit any unattended automation (cron job, LaunchAgent, GitHub Actions
  schedule, Cloudflare Worker cron, scheduled Claude task or routine, n8n flow,
  queue sender) against a 12-point reliability checklist, score it, and write
  the fixes. Use when the user says "is this automation solid", "harden this",
  "audit my automations", "why did this stop running", "automation checklist",
  before calling any new scheduled job done, or after a job failed silently.
when_to_use: Building, reviewing, or debugging anything that runs without a person watching.
---

# Automation hardening

An automation that works once is a demo. It is real when it keeps working while
nobody watches, and says so loudly when it does not. Most break in week two and
nobody notices for a month.

## The 12 checks

Score each item PASS, PARTIAL, FAIL or N/A, with the file and line that proves it.
Evidence only: "probably retries" is a FAIL.

| # | Check | PASS means |
|---|---|---|
| 1 | Error branch | Every step that can fail has a handled path: caught, logged, and routed to the alert. No bare `catch {}` or `|| true` that hides a failure the run depends on. |
| 2 | Retries | Transient failures (network, 429, 5xx) retry with backoff and a cap. Permanent failures (4xx, validation) do not retry. Retries are idempotent (see 6). |
| 3 | Alert when it stops | A missed run is detected, not only a failed one: a heartbeat or "last success" timestamp is checked by something else, and an overdue job pages a person (issue, email, push). Silence must be impossible. |
| 4 | Run log | Every run writes start, end, outcome, counts and duration somewhere durable and readable later (log file with rotation, D1 row, issue comment, Actions history). |
| 5 | Tested with bad data | The job was run against empty input, malformed input, a duplicate, an oversized item and a missing field, and behaves (skips with a log line, does not crash the batch or write garbage). |
| 6 | Duplicate check | Re-running the same window cannot double-send, double-post or double-charge: idempotency key, unique constraint, "seen" ledger or status column checked before the side effect. |
| 7 | Rate limits | Every external API call respects its documented limit (sleep, token bucket, batch size) and handles 429 with `Retry-After`. Limits written down next to the call. |
| 8 | Keys out of the workflow | No secret in code, config, logs or the prompt. Secrets come from the platform store (Actions secrets, Worker secrets, 1Password `op`, keychain), and logs redact them. Rotation path known. |
| 9 | Timeout | Every network call and the job as a whole have a timeout. A hung run cannot block the next one (lock with expiry, `concurrency` group, `timeout-minutes`). |
| 10 | Kill switch | One flag stops it without a deploy: a disabled setting, an env var, an empty queue that self-disables, a `paused` row. Documented where the user will look. |
| 11 | Human check on money and messages | Anything that sends email or DMs, posts publicly, moves money, or deletes data waits for an explicit approval, or is limited to a pre-approved queue. Default is draft, not send. |
| 12 | Cost cap | Paid calls (LLM tokens, APIs, SMS, compute) have a per-run and per-month ceiling enforced in code, with an alert before the cap. Free-tier limits counted the same way. |

## Procedure

1. **Inventory.** List every unattended job in scope. On this machine look at:
   `launchctl list | grep -v com.apple`, `~/Library/LaunchAgents/*.plist`,
   `crontab -l`, `.github/workflows/*.yml` with `schedule:` in each active repo,
   `wrangler.toml`/`wrangler.jsonc` `triggers.crons` in Worker repos, scheduled
   tasks (`mcp__scheduled-tasks__list_scheduled_tasks`), cloud routines, and
   anything the user names. Record: name, trigger, what it touches, side effects.
2. **Score.** For each job, read the code and config and fill the 12-row table
   with evidence. Read recent run history (Actions runs, log files, D1 rows) to
   confirm checks 3 and 4 hold in practice, not just in code.
3. **Rank fixes.** Order by blast radius: silent failure on anything that sends
   or spends first (3, 11, 12, 6), then data integrity (5, 6), then the rest.
4. **Fix.** One job per branch and PR (or per commit where the repo commits to
   main). Prove each fix: force the failure (bad input, revoked token, killed
   network, stopped schedule) and show the alert or the safe skip, then revert
   the forcing change.
5. **Report.** `AUTOMATION-AUDIT-<date>.md` in the repo or in
   `~/code/idea-intake/`: one scored table per job, the fixes made with links,
   and the open items.

## Rules

- Never weaken a gate to make a run pass.
- An alert nobody reads is a FAIL on 3. One issue per incident, updated, closed on recovery, beats a stream of emails.
- macOS cron cannot reach the keychain; jobs that need `gh`, `gws` or `op` run as LaunchAgents.
- A scheduled GitHub workflow is disabled after 60 days without repo activity; a monitor workflow must keep itself enabled or be watched by something else.
- Do not send, post or spend while testing. Use a dry-run flag or a sandbox account.
