# Stack checklist (manual + semi-automatic)

Scanners cannot see everything. Walk the sections that apply to the site's stack and
record each item as pass, fail or not applicable in the report. Severity is our
default; adjust with a reason. Verified 2026-10-10.

## Every site

| Check | How to detect | Sev |
|---|---|---|
| No secrets in git history or build output | scan.sh (betterleaks/trufflehog, checks.py) | Critical |
| No secret in a public env prefix (`NEXT_PUBLIC_`, `VITE_`, `PUBLIC_`, `EXPO_PUBLIC_`, `REACT_APP_`) | checks.py `public-env-secret`; grep build output for `sk_live_`, `rk_live_`, `sb_secret_`, `service_role`, `whsec_` | Critical |
| Framework and dependency patch level | osv-scanner; compare `npm ls next react astro vite` to the advisories pages | Critical |
| HTTPS enforced, HSTS, CSP, frame-ancestors, nosniff, Referrer-Policy | checks.py + Observatory | Medium |
| Host can actually send headers | GitHub Pages cannot (no custom headers, no 301s). Move to Cloudflare Pages (framework default) or put Cloudflare in front | Medium |
| No source maps, `.env`, `.git`, private intake or framework metadata served | checks.py exposed files + build output | High |
| Repo-root publishing (Umbo, Meantime) exposes nothing private | Every file in the repo is public: checks.py `--built <repo root>` | High |
| Third-party scripts inventoried and justified | checks.py `script-inventory` | Low (Medium on payment pages: PCI DSS 4.0.1) |
| CI workflows: actions pinned to SHAs, `permissions:` set, no `pull_request_target` checkout of PR code, no `${{ github.event.* }}` in `run:` | checks.py + zizmor | High |
| Install hardening: lockfile committed, `npm ci`, `ignore-scripts`, release-age delay | checks.py; `templates/npmrc` | Medium |
| security.txt present | checks.py | Info |
| Email DNS: SPF valid, DMARC published and moving past p=none | checkdmarc | Medium |
| Forms: CAPTCHA token verified server-side (Turnstile siteverify is mandatory; tokens single-use, 300 s) | grep widget vs `siteverify` call | High |
| Privacy policy when forms or analytics collect data; no non-essential cookies before consent for EU visitors | footer link; fresh-profile cookie check | Medium |

## Next.js (App Router)

| Check | How to detect | Sev |
|---|---|---|
| On a patched release: >= 15.5.24 or >= 16.3.3 (Aug 2026 RCE advisories); React RSC packages patched | `npm ls next react-server-dom-webpack`; https://github.com/vercel/next.js/security/advisories | Critical |
| Auth not enforced only in `middleware`/`proxy.ts` | each `'use server'` file re-checks session and ownership | High |
| Server Actions validate input (schema) and authorize | review every `'use server'` export | High |
| DB access in a `server-only` data layer; actions return DTOs, not raw rows | grep `import 'server-only'`; actions that `return db.` | Medium |
| `serverActions.allowedOrigins` minimal | `next.config.*` | Medium |
| CSP via `headers()` or nonce in `proxy.ts` (nonces force dynamic rendering) | curl headers | Medium |
| `productionBrowserSourceMaps` not enabled | `next.config.*` | Medium |
| Static export (`output: 'export'`) on a static host: server-side advisories mostly do not apply, but still upgrade | `next.config.*` | Note |

## Vite / React SPA / Astro

| Check | How to detect | Sev |
|---|---|---|
| No secrets in `VITE_*` / Astro `PUBLIC_*`; Astro secrets via `astro:env` `access: "secret"` | grep | Critical |
| `build.sourcemap` off or `hidden` | `vite.config.*` | Medium |
| React: no unsanitized `dangerouslySetInnerHTML`; react-markdown with `rehype-raw` needs `rehype-sanitize` | checks.py `xss-sink`; grep `rehype-raw`, `urlTransform` | High |
| Astro: `security.checkOrigin` not disabled; `security.allowedDomains` behind a proxy; `image.remotePatterns` not `**` | `astro.config.*` | High / Medium |
| Astro on a patched release (Jun-Jul 2026 advisories: SSRF, XSS, auth bypass in 6.4.7) | osv-scanner; https://github.com/withastro/astro/security/advisories | High (SSR only) |

## Supabase

| Check | How to detect | Sev |
|---|---|---|
| Security Advisor clean | `supabase db advisors` (CLI 2.81.3+), or MCP `get_advisors` type security | Critical (0013, 0002, 0023) |
| RLS enabled on every table in exposed schemas; unneeded anon/authenticated grants revoked | `select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where nspname='public' and relkind='r' and not relrowsecurity;` | Critical |
| Policies use `app_metadata`, never `user_metadata` | `grep -rn user_metadata supabase/migrations` | High |
| Views use `security_invoker = true` | migrations | High |
| service_role / `sb_secret_` key only server-side; plan migration off legacy JWT keys (deprecated by end of 2026) | scan.sh | Critical |
| Storage policies per user folder; public buckets hold only public files | dashboard / migrations | High |
| Auth: email confirmation, OTP expiry <= 1 h, custom SMTP, CAPTCHA, rate limits, MFA for admins, leaked-password protection (Pro) | dashboard | Medium-High |

## Hosting

| Host | Check | Sev |
|---|---|---|
| GitHub Pages | Cannot set headers or 301s: document the gap or move | Medium |
| Cloudflare Pages | Preview URLs are public: enable Access policy; `_headers` file for headers; Bot Fight Mode free | Medium-High |
| Vercel | Deployment Protection on previews; Secret env vars; production-only scopes; firewall bot rulesets off by default | Medium-High |
| Netlify | Secret scanning on (do not set `SECRETS_SCAN_ENABLED=false`); env scopes (Pro) | Medium |

## Payments (Stripe)

| Check | How to detect | Sev |
|---|---|---|
| Webhooks verified on the raw body with `Stripe-Signature` + `whsec_`, tolerance not 0, deduped by event ID | grep `constructEvent` near each webhook route; no `req.json()` before verify | Critical |
| Amounts decided server-side; fulfil from webhooks | grep `amount:` from `req.body`/`formData` | Critical |
| Restricted keys (`rk_`) where possible; only `pk_` in the browser | scan.sh | High |
| Payment pages: CSP covering Stripe's documented directives; script inventory (PCI DSS 4.0.1 SAQ A) | checks.py inventory; https://docs.stripe.com/security/guide | Medium |

## Auth providers, APIs, uploads

| Check | Sev |
|---|---|
| Clerk: protect at the resource, not only middleware; set `authorizedParties` | High |
| Auth.js: `AUTH_SECRET` 32+ random chars; `AUTH_TRUST_HOST` only behind a trusted proxy; separate dev/prod OAuth apps | High |
| CORS: allowlist + `Vary: Origin`; never reflect arbitrary Origin with credentials; never trust `Origin: null` | High |
| SSRF: user-supplied URLs fetched server-side are allowlisted, redirects off, private IP ranges and 169.254.169.254 blocked | High |
| Uploads: extension allowlist, magic-byte check, UUID names, size caps, separate storage host, auth required | High |
| Rate limits on auth, email and expensive endpoints (decide Upstash fail-open behaviour) | Medium |
| AI features: map to OWASP LLM Top 10 2026 and Agentic Top 10 (prompt injection, excessive agency, output handling) | High |

## Desktop and mobile

| Check | Sev |
|---|---|
| Tauri v2: capabilities scoped to window labels, no `"windows": ["*"]`, minimal `remote.urls`, CSP set in config, no CDN scripts | High |
| Expo / React Native: no secrets in `EXPO_PUBLIC_`; tokens in SecureStore, not AsyncStorage; map to MASVS | High |

## Sources
Next.js data security https://nextjs.org/docs/app/guides/data-security; Next.js CSP https://nextjs.org/docs/app/guides/content-security-policy;
Vite env https://vite.dev/guide/env-and-mode; Astro config https://docs.astro.build/en/reference/configuration-reference/;
Supabase advisors https://supabase.com/docs/guides/database/database-advisors; RLS https://supabase.com/docs/guides/database/postgres/row-level-security;
API keys https://supabase.com/docs/guides/api/api-keys; Stripe webhooks https://docs.stripe.com/webhooks; Stripe keys https://docs.stripe.com/keys;
Turnstile https://developers.cloudflare.com/turnstile/get-started/server-side-validation/; Cloudflare previews https://developers.cloudflare.com/pages/configuration/preview-deployments/;
Vercel protection https://vercel.com/docs/deployment-protection; OWASP cheat sheets (uploads, SSRF) https://cheatsheetseries.owasp.org/;
Tauri https://v2.tauri.app/security/capabilities/; Expo SecureStore https://docs.expo.dev/versions/latest/sdk/securestore/
