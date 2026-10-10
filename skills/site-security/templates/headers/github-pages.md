# GitHub Pages and security headers

GitHub Pages cannot send custom response headers or real 301 redirects. That means no
HSTS (beyond GitHub's own), no CSP header, no frame-ancestors, no Permissions-Policy.

Options, best first:
1. **Move to Cloudflare Pages** (framework default per SUMMIT-246) and use `_headers`.
2. **Keep Pages, proxy through Cloudflare**: orange-cloud the DNS record and add a
   Transform Rule (Modify Response Header) with the headers from `_headers`.
3. **Stopgap**: a `<meta http-equiv="Content-Security-Policy" content="...">` in every
   page head. Covers script/style sources only; cannot set frame-ancestors, HSTS or
   reporting.

Always enable "Enforce HTTPS" in the repository's Pages settings.
