# Keeping the security tooling current

Security tooling goes stale quietly: flags change, tools get archived or compromised,
new framework advisories land. Run this monthly, and immediately when a critical advisory
hits a framework we use.

## Monthly refresh (about 30 minutes with Claude)
1. **Tool versions and flags.** `brew outdated`; `bash scripts/install-tools.sh`; for each
   tool in `tools.md` check its releases page for breaking changes. Run `tests/run-fixture.sh`
   (covers the built-in checks, redaction and failure handling), then one real
   `scan.sh --mode audit` against summitsoftwaresolutions.dev and confirm every installed
   tool shows `ran` in `summary.md`. A tool that changed its flags shows up as `failed`
   with its stderr in `logs/`. Bump the pinned Observatory version in `scan.sh`
   (pick a release at least two weeks old).
2. **Tool health.** Search "<tool> compromised", "<tool> archived", "<tool> license change"
   for each core tool. 2025-26 precedents: Trivy Actions hijack (Mar 2026), Semgrep MCP
   archived (Oct 2025), gitleaks feature-frozen in favour of Betterleaks, Semgrep rules
   license change.
3. **Framework advisories** (check each one we ship):
   - Next.js https://github.com/vercel/next.js/security/advisories
   - React https://github.com/facebook/react/security/advisories
   - Vite https://github.com/vitejs/vite/security/advisories
   - Astro https://github.com/withastro/astro/security/advisories
   - Supabase https://supabase.com/security and Security Advisor emails
   - Vercel bulletins https://vercel.com/kb/bulletin/
4. **Feeds.** OSV (via osv-scanner, already per scan), GitHub Advisory DB
   (`gh api /advisories?ecosystem=npm&severity=critical&per_page=50`), CISA KEV JSON
   (normalize.py caches it daily). Do not rely on NVD alone (priority-only enrichment since
   2026-04-15).
5. **npm ecosystem.** Watch for worm-style compromises (Shai-Hulud Sep/Nov 2025, axios Mar
   2026, keyv/cacheable Aug 2026). After any: run osv-scanner on every repo the same day.
6. **Standards.** OWASP Top 10 / ASVS / LLM Top 10 revisions; update `standards.md`.
7. **Record it.** Update the "Last verified" line in `SKILL.md` and `tools.md`, note changes
   in the commit message (`chore(site-security): monthly tooling refresh`).

## Emergency path (critical advisory in a framework we ship)
1. List affected repos: run osv-scanner across all site repos (or `summit audit --all`).
2. Decide exposure per repo (e.g. static export vs server runtime).
3. One PR per repo with the patch upgrade; deploy; re-scan.
4. Note it in the monthly client report.
