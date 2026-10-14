# Resolution playbook

How to fix each finding class. One fix per PR, smallest change that removes the cause,
verified by re-running the tool that found it. Anything needing an account owner
(rotation, DNS, host settings, billing) becomes a checklist item for Ryan, not a guess.

## Exposed secret (any `secret-*`, `tracked-env`, `tracked-key`, trufflehog/betterleaks)
1. **Rotate first.** Revoke the key at the provider and issue a new one (Stripe dashboard,
   Supabase API keys, AWS IAM, GitHub tokens). A secret that was ever in a public repo or
   served file is compromised regardless of how long it was there.
2. Put the new value in the host's secret store (Vercel Secret env var, Cloudflare/Netlify
   env, GitHub Actions secret) and read it server-side only.
3. Remove it from code; `git rm --cached` tracked env files; add `.env`, `.env.*`,
   `!.env.example` to `.gitignore`.
4. If the repo is or was public, purge history (`git filter-repo --invert-paths --path .env`)
   and ask GitHub to clear cached views; force-push only with Ryan's approval.
5. Check provider logs for use of the old key during the exposure window.
6. Add the gitleaks/betterleaks pre-commit hook (`templates/pre-commit-config.yaml`).

## Secret in a public env prefix (`public-env-secret`)
Rename without the prefix (e.g. `SUPABASE_SERVICE_ROLE_KEY`), move the code that uses it
to a server route, Server Action, edge function or Astro `astro:env` server secret. Rotate
it if any build with the old name was deployed.

## Vulnerable dependency (`osv-scanner`, `npm-audit`)
1. KEV-tagged or critical with a reachable code path: fix today.
2. Direct dependency: bump to the first fixed version on the same major
   (`npm install pkg@x.y.z`), run build and tests.
3. Transitive: update the parent; if none, add an `overrides` (npm) / `pnpm.overrides`
   entry pinned to the fixed version, with a comment linking the advisory.
4. Dev-only or not reachable (e.g. Vite dev-server bug on a static build): still upgrade,
   but severity can drop; record why.
5. Malicious package (`MAL-` IDs): treat the machine and CI that installed it as
   compromised; rotate every credential they held.

## Missing or weak security headers (`hsts`, `csp`, `clickjacking`, `xcto`, ...)
Use the host template in `templates/headers/`:
- Cloudflare Pages / Netlify: `_headers` in the publish directory.
- Vercel: `headers` in `vercel.json`.
- Next.js: `headers()` in `next.config.js` (static), nonce CSP in `proxy.ts` (dynamic).
- GitHub Pages: cannot set headers. Options, in order: move to Cloudflare Pages (framework
  default), proxy through Cloudflare with a Transform Rule, or a `<meta>` CSP as a partial
  stopgap (no HSTS, no frame-ancestors).
CSP rollout: ship `Content-Security-Policy-Report-Only` first, collect violations for a
week (browser console or a small reporting endpoint), adjust, then enforce.

## Exposed file or source map (`exposed-file`, `publish-forbidden-file`, `source-map`)
Exclude it from the build output (Vite `build.sourcemap: false|'hidden'`, Next
`productionBrowserSourceMaps: false`). For repo-root publishing, move private files out of
the repo or switch to publishing a build directory. Rotate anything a leaked file held.

## CI workflow issues (`unpinned-action`, `workflow-injection`, `prt-checkout`, zizmor)
- Pin each third-party action to its full commit SHA with the version as a comment:
  `uses: owner/action@<40-char-sha> # v1.2.3`. Resolve a tag's SHA with
  `gh api repos/OWNER/REPO/commits/vX.Y.Z --jq .sha`. Let Dependabot/Renovate bump SHAs.
- Move `${{ github.event.* }}` text into `env:` and reference `"$VAR"` in `run:`.
- Add top-level `permissions: contents: read`; grant more per job only as needed.
- Never check out PR head code in `pull_request_target`.

## Supply-chain hardening (`no-lockfile`, `loose-version`)
Commit the lockfile; CI installs with `npm ci` or `pnpm install --frozen-lockfile`; add
`templates/npmrc` (`ignore-scripts=true`, `min-release-age=3` on npm 11.10+); pnpm:
`minimumReleaseAge: 4320`, `trustPolicy: no-downgrade`; Renovate preset
`security:minimumReleaseAgeNpm` or Dependabot `cooldown`. Packages that need install
scripts (esbuild, sharp) get an explicit allowlist.

## Cookies (`cookie-flags`)
Session/auth cookies: `Secure; HttpOnly; SameSite=Lax` (or `Strict`). Fix in the auth
library config, not by hand-editing responses.

## Mixed content, third-party scripts without SRI
Load over https or self-host. Pinned CDN files get `integrity` + `crossorigin="anonymous"`.
Stripe.js is exempt from SRI (must load from js.stripe.com); cover it in CSP.

## Email DNS (`spf`, `dmarc`, `dmarc-policy`)
Publish one SPF record listing every sender; DMARC `p=none` with a report address, review
for 2-4 weeks, then `quarantine`, then `reject`. Changes are DNS: Ryan or the client does
them; capture the existing zone first (SUMMIT-252 cutover rules).

## Supabase advisor lints
- 0013 RLS disabled: `alter table ... enable row level security;` plus explicit policies.
- 0010 security definer view: `alter view ... set (security_invoker = true);`
- 0015 user_metadata in policy: switch to `app_metadata` (set server-side).
- 0025 public bucket listing: make the bucket private or add a restrictive list policy.
Ship each as a migration in its own PR; test with the anon key that access is denied.

## TLS (`testssl`)
Fix at the host or CDN (minimum TLS 1.2, modern ciphers). Managed hosts usually already
comply; findings there often mean an old origin behind a proxy.

## After every fix
Re-run `scan.sh` (same mode, same targets). The finding must disappear while the tool
shows `ran`. Update the report's status and close the Jira item.
