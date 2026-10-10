# Tools: what we use, why, and what to watch

Last verified: **2026-10-10** (two research rounds against primary sources). Re-verify
monthly per `update-watch.md`. "Version" is the latest seen on that date.

## Core toolchain (run by scan.sh)

| Tool | Role | Version | License | Install | Notes |
|---|---|---|---|---|---|
| summit checks (`checks.py`) | Headers, CSP, cookies, HTTPS redirect, exposed files, source maps, secrets in served JS and build output, security.txt, tracked env files, public env vars that look secret, unpinned or injectable workflows, lockfile | 0.1.0 | Summit | bundled | Python stdlib only; works on any stack including no-build sites |
| Betterleaks | Secrets in git history and build output | 1.7.3 | MIT | `brew install betterleaks` | From the gitleaks author. Reads `.gitleaks.toml` and `.gitleaksignore`. Pin v1.7.x CLI syntax: the unreleased v2 renames `dir` to `filesystem` |
| gitleaks (fallback) | Same | 8.30.1 | MIT | `brew install gitleaks` | Feature complete, security patches only. `git` and `dir` subcommands; `-f/--report-format`, `-r/--report-path`, `--redact`, `--exit-code` |
| TruffleHog | Secrets, with live verification | 3.97.x | AGPL-3.0 | `brew install trufflehog` | `--results=verified,unknown` cuts false positives. Run from outside the repo for `git file://` |
| OSV-Scanner | Known-vulnerable dependencies (19+ lockfile types) | 2.6.0 | Apache-2.0 | `brew install osv-scanner` | `scan source -r --format json --output-file`. Exit 1 = vulns, 128 = no manifests. `osv-scanner fix` suggests upgrades |
| Semgrep CE | Static analysis | 1.180.0 | LGPL-2.1 engine; registry rules under Semgrep Rules License (internal use OK, no redistribution) | `brew install semgrep` | Always `--metrics=off`. Opengrep is the community fork if licensing tightens. Semgrep MCP repo archived 2025-10-28 |
| zizmor | GitHub Actions workflow audit (injection, permissions, unpinned, impostor commits) | 1.30.1 | MIT | `brew install zizmor` | Exit 11-14 = findings by severity |
| MDN HTTP Observatory | Header grade and tests | current | MPL-2.0 | `npx @mdn/mdn-http-observatory <host>` | JSON out. API v2: `POST https://observatory-api.mdn.mozilla.net/api/v2/scan?host=`; 1 scan per host per minute |
| testssl.sh | TLS configuration | 3.2.4 | GPL-2.0 | `brew install testssl` | `--jsonfile`. Slow (1-3 min); audit and monitor modes only |
| ZAP baseline | Passive DAST (spider + passive rules, no attacks) | `ghcr.io/zaproxy/zaproxy:stable`; action-baseline v0.15.0 | Apache-2.0 | Docker | Part of Checkmarx since 2024-09, still open source. Full scan attacks the target: staging only |
| Nuclei | Exposure and misconfiguration templates | current | MIT | `brew install nuclei` | Opt-in `--active`, `-rl 10`. Breaking changes between releases |
| checkdmarc | SPF, DMARC, MTA-STS, DNSSEC | current | Apache-2.0 | `pipx install checkdmarc` | DKIM needs selector names, not checked |
| npm audit | Dependency fallback when OSV-Scanner is absent | npm 11 | Artistic-2.0 | bundled with Node | `npm audit signatures` checks provenance (provenance is not proof of safety: the Aug 2026 keyv worm shipped with valid provenance) |

## Recommended alongside

| Tool | Use | Notes |
|---|---|---|
| Anthropic `security-guidance` plugin | Advisory checks on each edit, turn and commit Claude makes | All plans. Never blocks; use hooks for hard blocks |
| Anthropic `/claude-security` plugin | Deep multi-agent code review, SARIF + JSONL + patches | Paid plans or API. Patches never auto-applied; results vary run to run |
| `/security-review` | One pass over the current branch diff | Built into Claude Code |
| anthropics/claude-code-security-review Action | PR review comments | Not hardened against prompt injection: trusted PRs only. Override the default model (still Opus 4.1) |
| Trail of Bits skills (`/plugin marketplace add trailofbits/skills`) | insecure-defaults, supply-chain-risk-auditor, differential-review, static-analysis | Reputable security firm; review before installing |
| Snyk MCP | SAST/SCA from Claude | Free tier: 100 Code tests/month |
| GitHub MCP server (`--read-only`) | Dependabot and advisory data | Official |
| Syft | SBOM (CycloneDX/SPDX) | For client handoff or PCI inventories |
| Socket Firewall Free (`npm i -g sfw`) | Blocks confirmed malware at install time | Telemetry cannot be disabled |
| Uptime Kuma (self-hosted) or UptimeRobot paid | Uptime, keyword (defacement) and certificate monitoring | UptimeRobot free tier is limited to non-commercial use. Let's Encrypt ended expiry emails 2025-06-04; use Red Sift Certificates Lite (free) |
| Supabase CLI `supabase db advisors` | Security Advisor lints | CLI 2.81.3+. `supabase db lint` is plpgsql_check, not security |

## Not used, and why

| Tool | Reason |
|---|---|
| CodeQL on private repos | License requires a paid GitHub Advanced Security / Code Security seat ($30/committer/month) |
| GitHub Secret Protection | $19/committer/month for private repos; free scanners cover it |
| Trivy GitHub Actions | March 2026 compromise (CVE-2026-33634): tags force-pushed with a credential stealer. If ever used: trivy-action >= v0.35.0, pinned by SHA |
| Semgrep MCP (`semgrep/mcp`) | Archived; use the CLI |
| securityheaders.com API | Discontinued for new subscribers |
| SSL Labs API v4 | Requires an organization email (no Gmail); testssl covers it |
| StackHawk | No free tier (Wingman $10/user/month) |
| Burp Community | Manual only, no scanner |
| Report URI | No free tier ($54.99/month); point CSP `report-to` at a small Supabase edge function instead if reporting is needed |

## Sources
- https://github.com/betterleaks/betterleaks, https://github.com/gitleaks/gitleaks
- https://github.com/trufflesecurity/trufflehog
- https://google.github.io/osv-scanner/usage/, https://github.com/google/osv-scanner
- https://github.com/semgrep/semgrep, https://semgrep.dev/legal/rules-license, https://github.com/semgrep/mcp
- https://docs.zizmor.sh/usage/
- https://github.com/mdn/mdn-http-observatory, https://developer.mozilla.org/en-US/observatory/docs/faq
- https://github.com/testssl/testssl.sh
- https://www.zaproxy.org/docs/docker/baseline-scan/, https://github.com/zaproxy/action-baseline
- https://github.com/projectdiscovery/nuclei
- https://github.com/domainaware/checkdmarc
- https://code.claude.com/docs/en/security-guidance, https://code.claude.com/docs/en/claude-security, https://github.com/anthropics/claude-code-security-review
- https://github.com/trailofbits/skills
- https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23
- https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md, https://github.com/security/plans
- https://letsencrypt.org/2025/06/26/expiration-notification-service-has-ended/
- https://supabase.com/docs/reference/cli/supabase-db-advisors
