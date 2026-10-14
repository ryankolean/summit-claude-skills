#!/usr/bin/env python3
"""Built-in, dependency-free security checks for Summit sites.

Runs three groups of checks and writes normalized findings JSON:
  --url    live checks against a deployed site (headers, TLS redirect, exposed
           files, source maps, secrets in served JS, security.txt, mixed content)
  --built  static checks against build output (secrets, files that must never
           be published, third-party script inventory, inline script count)
  --repo   repository checks (tracked env files, public env vars that look
           secret, unpinned GitHub Actions, risky workflow triggers, risky sinks)

Only scan sites you own or have written permission to test. Live checks send a
small number of GET requests (well under 60) at a polite pace.

Python 3.9+ standard library only. Output schema: see references/findings-schema.md
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html.parser
import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"
UA = f"summit-site-security/{VERSION} (owner-authorized scan)"
TIMEOUT = 15
PAUSE = 0.25  # seconds between live requests

FINDINGS: list[dict] = []
SKIPPED: list[dict] = []

# ---------------------------------------------------------------------------
# Secret patterns. Kept deliberately specific to limit false positives.
# Each: (id, title, regex, severity)
# ---------------------------------------------------------------------------
SECRET_PATTERNS = [
    ("stripe-live-secret", "Stripe live secret key", r"\bsk_live_[0-9A-Za-z]{16,}", "critical"),
    ("stripe-live-restricted", "Stripe live restricted key", r"\brk_live_[0-9A-Za-z]{16,}", "critical"),
    ("stripe-webhook-secret", "Stripe webhook signing secret", r"\bwhsec_[0-9A-Za-z]{20,}", "critical"),
    ("aws-access-key", "AWS access key ID", r"\b(AKIA|ASIA)[0-9A-Z]{16}\b", "critical"),
    ("github-token", "GitHub token", r"\b(ghp|gho|ghu|ghs|ghr)_[0-9A-Za-z]{36,}\b", "critical"),
    ("github-fine-grained", "GitHub fine-grained token", r"\bgithub_pat_[0-9A-Za-z_]{40,}\b", "critical"),
    ("private-key", "Private key block", r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY-----(?:\s|\\n)*[A-Za-z0-9+/=]{64,}", "critical"),
    ("slack-token", "Slack token", r"\bxox[abprs]-[0-9A-Za-z-]{10,}", "high"),
    ("openai-key", "OpenAI API key", r"\bsk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{20,}T3BlbkFJ[A-Za-z0-9_-]{20,}", "high"),
    ("anthropic-key", "Anthropic API key", r"\bsk-ant-[A-Za-z0-9_-]{32,}", "critical"),
    ("sendgrid-key", "SendGrid API key", r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}", "high"),
    ("resend-key", "Resend API key", r"\bre_[A-Za-z0-9]{8}_[A-Za-z0-9]{16,}", "high"),
    ("supabase-secret-key", "Supabase secret key", r"\bsb_secret_[A-Za-z0-9_-]{20,}", "critical"),
    ("npm-token", "npm access token", r"\bnpm_[A-Za-z0-9]{36}\b", "critical"),
    ("google-oauth-secret", "Google OAuth client secret", r"\bGOCSPX-[A-Za-z0-9_-]{20,}", "high"),
    ("shopify-token", "Shopify access token", r"\bshp(?:at|ca|pa|ss)_[a-fA-F0-9]{32}\b", "critical"),
    ("huggingface-token", "Hugging Face token", r"\bhf_[A-Za-z0-9]{30,}\b", "high"),
    ("db-url-credentials", "Database URL with embedded password", r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|rediss)://[^:/\s'\"]+:[^@\s'\"]{3,}@[^\s'\"]+", "critical"),
    ("google-api-key", "Google API key (often public; confirm restrictions)", r"\bAIza[0-9A-Za-z_-]{35}\b", "low"),
]
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")

TEXT_EXT = {".html", ".htm", ".js", ".mjs", ".cjs", ".json", ".map", ".txt", ".xml",
            ".css", ".ts", ".tsx", ".jsx", ".env", ".yml", ".yaml", ".toml", ".md",
            ".astro", ".vue", ".svelte", ".py", ".php", ".sql", ".sh", ".ini", ".vars"}
SECRET_ALLOW = re.compile(r"EXAMPLE|XXXXXXXX|[Yy]our[_-]?[Kk]ey|[Pp]laceholder|<[A-Z_]{3,}>")

# Files that must never be reachable on a live site or present in a publish dir.
EXPOSED_PATHS = [
    ("/.env", "env", "critical"),
    ("/.env.local", "env", "critical"),
    ("/.env.production", "env", "critical"),
    ("/.env.development", "env", "critical"),
    ("/.dev.vars", "env", "critical"),
    ("/.aws/credentials", "env", "critical"),
    ("/.htpasswd", "text", "high"),
    ("/.svn/entries", "text", "medium"),
    ("/backup.zip", "binary", "high"),
    ("/.git/HEAD", "git", "high"),
    ("/.git/config", "git", "high"),
    ("/.npmrc", "npmrc", "high"),
    ("/.DS_Store", "dsstore", "low"),
    ("/.vscode/settings.json", "json", "low"),
    ("/docker-compose.yml", "yaml", "medium"),
    ("/seo-god.json", "json", "low"),
    ("/.seo-god/secrets.env", "env", "critical"),
    ("/intake.json", "json", "high"),
    ("/private/intake.json", "json", "high"),
    ("/tasks/todo.md", "text", "low"),
    ("/AGENTS.md", "text", "info"),
    ("/CLAUDE.md", "text", "low"),
]
FORBIDDEN_PUBLISH_GLOBS = [
    (".env", "critical"), (".env.*", "critical"), ("*.pem", "critical"), ("*.key", "critical"),
    ("id_rsa*", "critical"), (".npmrc", "high"), ("*.sqlite", "high"), ("*.db", "medium"),
    ("intake*.json", "high"), ("*.private.*", "high"), ("*.map", "medium"), (".DS_Store", "low"),
    ("CLAUDE.md", "low"), ("tasks/todo.md", "low"), ("tasks/lessons.md", "low"),
]

PUBLIC_ENV_PREFIXES = ("NEXT_PUBLIC_", "NUXT_PUBLIC_", "VITE_", "PUBLIC_", "REACT_APP_", "EXPO_PUBLIC_", "GATSBY_")
PUBLIC_ENV_RE = re.compile(r"\b((?:NEXT_PUBLIC_|NUXT_PUBLIC_|VITE_|PUBLIC_|REACT_APP_|EXPO_PUBLIC_|GATSBY_)[A-Z0-9_]+)")
SECRETISH = re.compile(r"(SECRET|SERVICE_ROLE|PRIVATE_KEY|PASSWORD|PASSWD|(?:^|_)SK(?:_|$)|WEBHOOK|(?:^|_)TOKEN(?:_|$))")
PUBLIC_OK = re.compile(r"MAPBOX|PUBLISHABLE|ANON|SITE_KEY|SITEKEY|RECAPTCHA_KEY|TURNSTILE")


def add(category: str, check: str, severity: str, title: str, location: str,
        evidence: str = "", fix: str = "", refs: list[str] | None = None) -> None:
    fid = hashlib.sha1(f"{check}|{location}|{title}".encode()).hexdigest()[:12]
    FINDINGS.append({
        "id": f"builtin-{fid}",
        "tool": "summit-checks",
        "check": check,
        "category": category,
        "severity": severity,
        "title": title,
        "location": location,
        "evidence": redact(evidence)[:300],
        "fix": fix,
        "references": refs or [],
    })


def skip(check: str, reason: str) -> None:
    SKIPPED.append({"check": check, "reason": reason})


def redact(text: str) -> str:
    """Never write a full secret to disk. Keep a short prefix for triage."""
    if not text:
        return ""
    def _r(m: re.Match) -> str:
        s = m.group(0)
        return s[:8] + "…[redacted " + str(len(s)) + " chars]"
    for _, _, pat, _ in SECRET_PATTERNS:
        text = re.sub(pat, _r, text)
    text = JWT_RE.sub(_r, text)
    # KEY=value and KEY: value lines (env files, configs): keep the key, drop the value
    text = re.sub(r"(?m)^(\s*[A-Za-z_][A-Za-z0-9_.-]*\s*(?:=|:\s))(?!//)\S.*$", r"\1[redacted]", text)
    # credentials inside URLs
    text = re.sub(r"://([^:/\s]+):[^@\s]+@", r"://\1:[redacted]@", text)
    return text


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


def fetch(url: str, follow: bool = True, max_bytes: int = 2_000_000):
    """Return (status, headers(dict-like, lowercased keys -> list), body bytes, final_url)."""
    time.sleep(PAUSE)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    ctx = ssl.create_default_context()
    handlers = [urllib.request.HTTPSHandler(context=ctx)]
    if not follow:
        handlers.append(NoRedirect())
    opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(req, timeout=TIMEOUT) as resp:
            body = resp.read(max_bytes)
            return resp.status, _hdrs(resp.headers), body, resp.geturl()
    except urllib.error.HTTPError as e:
        body = b""
        try:
            body = e.read(max_bytes)
        except Exception:
            pass
        return e.code, _hdrs(e.headers), body, url
    except Exception as e:  # network, TLS, DNS
        return None, {}, str(e).encode(), url


def _hdrs(h) -> dict:
    out: dict[str, list[str]] = {}
    if h is None:
        return out
    for k, v in h.items():
        out.setdefault(k.lower(), []).append(v)
    return out


def h1(headers: dict, name: str) -> str | None:
    v = headers.get(name.lower())
    return v[0] if v else None


class AssetParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts: list[dict] = []
        self.inline_scripts = 0
        self.http_refs: list[str] = []
        self.meta_csp: str | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            if a.get("src"):
                self.scripts.append({"src": a["src"], "integrity": a.get("integrity")})
            else:
                self.inline_scripts += 1
        if tag == "meta" and (a.get("http-equiv") or "").lower() == "content-security-policy":
            self.meta_csp = a.get("content")
        for attr in ("src", "href"):
            val = a.get(attr) or ""
            if val.startswith("http://") and tag in ("script", "img", "iframe", "link", "source", "video", "audio"):
                self.http_refs.append(val)


# ---------------------------------------------------------------------------
# Live URL checks
# ---------------------------------------------------------------------------
def check_url(url: str) -> None:
    if not re.match(r"^https?://", url):
        url = "https://" + url
    parsed = urllib.parse.urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    status, headers, body, final = fetch(url)
    if status is None:
        add("availability", "fetch", "high", "Site could not be fetched", url, body.decode(errors="ignore"),
            "Check DNS, TLS certificate and hosting.")
        return
    fparsed = urllib.parse.urlparse(final)
    if fparsed.scheme != "https":
        add("transport", "https", "high", "Site does not end on HTTPS", final, "",
            "Serve the site over HTTPS and redirect HTTP to HTTPS.")

    # HTTP -> HTTPS redirect
    st, hh, _, _ = fetch(f"http://{parsed.netloc}/", follow=False)
    loc = h1(hh, "location") or ""
    if st is None:
        skip("http-redirect", "HTTP port not reachable (fine if only HTTPS is served)")
    elif not (300 <= st < 400 and loc.startswith("https://")):
        add("transport", "http-redirect", "medium", "HTTP does not redirect to HTTPS",
            f"http://{parsed.netloc}/", f"status {st} location {loc!r}",
            "Enable 'Enforce HTTPS' at the host (GitHub Pages, Cloudflare, Netlify, Vercel all support it).")

    check_headers(final, headers)
    check_cookies(final, headers)

    page = body.decode("utf-8", errors="ignore")
    p = AssetParser()
    try:
        p.feed(page)
    except Exception:
        pass
    if p.meta_csp and not h1(headers, "content-security-policy"):
        add("headers", "csp-meta", "info", "CSP delivered by <meta> tag only", final, p.meta_csp[:200],
            "A meta CSP cannot set frame-ancestors, report-to or sandbox. Move CSP to a response header when the host allows it.")
        analyze_csp(p.meta_csp, final, via="meta")
    for ref in sorted(set(p.http_refs))[:10]:
        add("transport", "mixed-content", "medium", "Insecure http:// resource on an HTTPS page", final, ref,
            "Load the resource over https:// or self-host it.")
    for s in p.scripts:
        src = urllib.parse.urljoin(final, s["src"])
        if urllib.parse.urlparse(src).netloc not in ("", fparsed.netloc) and not s["integrity"]:
            host = urllib.parse.urlparse(src).netloc
            sev = "info" if host.endswith("stripe.com") else "low"
            add("client-side", "third-party-script", sev, f"Third-party script without Subresource Integrity: {host}",
                final, src,
                "Pin a version and add integrity + crossorigin, or self-host. Stripe.js is exempt (must load from js.stripe.com, changes continuously); cover it with CSP instead.",
                ["https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity"])

    check_served_js(final, fparsed.netloc, p.scripts)
    check_exposed_paths(origin)
    check_security_txt(origin)
    check_cors(final)
    if fparsed.scheme == "https":
        check_cert(fparsed.hostname or parsed.hostname, fparsed.port or 443)


def check_headers(url: str, headers: dict) -> None:
    hsts = h1(headers, "strict-transport-security")
    if not hsts:
        add("headers", "hsts", "medium", "Missing Strict-Transport-Security header", url, "",
            "Send Strict-Transport-Security: max-age=31536000; includeSubDomains (add preload only for domains you control long term). GitHub Pages cannot set this header; use Cloudflare in front or move hosting.",
            ["https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security"])
    else:
        m = re.search(r"max-age=(\d+)", hsts)
        if not m or int(m.group(1)) < 15552000:
            add("headers", "hsts", "low", "HSTS max-age below 180 days", url, hsts, "Use max-age=31536000.")

    csp = h1(headers, "content-security-policy")
    csp_ro = h1(headers, "content-security-policy-report-only")
    if not csp:
        sev = "low" if csp_ro else "medium"
        add("headers", "csp", sev, "Missing Content-Security-Policy header" + (" (report-only present)" if csp_ro else ""),
            url, csp_ro or "",
            "Start with Content-Security-Policy-Report-Only, inventory scripts, then enforce. Minimum: default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'. Payment pages: PCI DSS 4.0.1 (SAQ A) expects protection against script attacks; Stripe documents the CSP directives Checkout and Elements need.",
            ["https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP", "https://docs.stripe.com/security/guide#content-security-policy"])
    else:
        analyze_csp(csp, url, via="header")

    if (h1(headers, "x-content-type-options") or "").lower() != "nosniff":
        add("headers", "xcto", "low", "Missing X-Content-Type-Options: nosniff", url, "", "Send X-Content-Type-Options: nosniff.")
    if not h1(headers, "referrer-policy"):
        add("headers", "referrer-policy", "low", "Missing Referrer-Policy header", url, "",
            "Send Referrer-Policy: strict-origin-when-cross-origin.")
    if not h1(headers, "permissions-policy"):
        add("headers", "permissions-policy", "info", "Missing Permissions-Policy header", url, "",
            "Send Permissions-Policy: camera=(), microphone=(), geolocation=() (adjust to what the site uses).")
    framing_ok = h1(headers, "x-frame-options") or (csp and "frame-ancestors" in csp)
    if not framing_ok:
        add("headers", "clickjacking", "medium", "No clickjacking protection (X-Frame-Options or CSP frame-ancestors)",
            url, "", "Send CSP frame-ancestors 'self' (preferred) or X-Frame-Options: SAMEORIGIN.")
    for name in ("server", "x-powered-by", "x-aspnet-version"):
        v = h1(headers, name)
        if v and re.search(r"\d", v):
            add("headers", "version-disclosure", "info", f"{name} header discloses a version", url, f"{name} {v}",
                "Remove version numbers from server headers where the host allows it.")


def analyze_csp(csp: str, url: str, via: str) -> None:
    directives = {}
    for part in csp.split(";"):
        part = part.strip()
        if not part:
            continue
        bits = part.split()
        directives[bits[0].lower()] = [b.lower() for b in bits[1:]]
    script = directives.get("script-src") or directives.get("default-src") or []
    if "script-src" not in directives and "default-src" not in directives:
        add("headers", "csp-weak", "medium", "CSP does not restrict scripts (no script-src or default-src)", url, csp[:200],
            "Add default-src 'self' (and script-src for any other script hosts).")
    has_nonce_or_hash = any(t.startswith("'nonce-") or t.startswith("'sha") for t in script)
    strict_dynamic = "'strict-dynamic'" in script and has_nonce_or_hash
    if "'unsafe-inline'" in script and not has_nonce_or_hash:
        add("headers", "csp-weak", "medium", "CSP allows 'unsafe-inline' scripts", url, csp[:200],
            "Replace 'unsafe-inline' with nonces or hashes (Next.js supports nonces via middleware; static sites can hash inline scripts at build time).")
    if "'unsafe-eval'" in script:
        add("headers", "csp-weak", "low", "CSP allows 'unsafe-eval'", url, csp[:200], "Remove 'unsafe-eval' unless a dependency truly needs it.")
    if not strict_dynamic and any(t in ("*", "http:", "https:", "data:") for t in script):
        add("headers", "csp-weak", "medium", "CSP script-src allows any host or scheme", url, csp[:200],
            "List specific script hosts instead of *, https: or data:.")
    if "object-src" not in directives and "'none'" not in (directives.get("default-src") or []):
        add("headers", "csp-weak", "low", "CSP has no object-src 'none'", url, csp[:200], "Add object-src 'none'.")
    if "base-uri" not in directives:
        add("headers", "csp-weak", "low", "CSP has no base-uri", url, csp[:200], "Add base-uri 'self'.")


def check_cookies(url: str, headers: dict) -> None:
    for c in headers.get("set-cookie", []):
        name = c.split("=", 1)[0].strip()
        attrs = {a.strip().split("=", 1)[0].lower() for a in c.split(";")[1:]}
        missing = [f for f in ("Secure", "HttpOnly", "SameSite") if f.lower() not in attrs]
        if missing:
            sev = "medium" if re.search(r"sess|auth|token|sid", name, re.I) else "low"
            flags = c[c.find(";"):] if ";" in c else ""
            add("cookies", "cookie-flags", sev, f"Cookie {name} missing {', '.join(missing)}", url, f"{name}=[redacted]{flags}"[:160],
                "Set Secure; HttpOnly; SameSite=Lax (or Strict) on session and auth cookies.")


def scan_text_for_secrets(text: str, location: str, category: str = "secrets") -> None:
    for sid, title, pat, sev in SECRET_PATTERNS:
        for m in re.finditer(pat, text):
            if SECRET_ALLOW.search(m.group(0)):
                continue
            add(category, f"secret-{sid}", sev, f"{title} exposed", location, m.group(0),
                "Revoke and rotate the key now, remove it from the code and history, and load it from a server-side environment variable.")
            break
    for m in JWT_RE.finditer(text):
        role = jwt_role(m.group(0))
        if role == "service_role":
            add(category, "secret-supabase-service-role", "critical", "Supabase service_role key exposed", location, m.group(0),
                "Rotate the service_role key in Supabase now. It bypasses Row Level Security and must only live server-side.",
                ["https://supabase.com/docs/guides/api/api-keys"])
            break


def jwt_role(token: str) -> str | None:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        return data.get("role")
    except Exception:
        return None


def check_served_js(page_url: str, host: str, scripts: list[dict]) -> None:
    same = [urllib.parse.urljoin(page_url, s["src"]) for s in scripts]
    same = [u for u in same if urllib.parse.urlparse(u).netloc == host][:12]
    if not same:
        skip("served-js", "no same-origin scripts found on the homepage")
    for js in same:
        st, hh, body, _ = fetch(js, max_bytes=5_000_000)
        if st != 200:
            continue
        text = body.decode("utf-8", errors="ignore")
        scan_text_for_secrets(text, js, "secrets")
        m = re.search(r"sourceMappingURL=([^\s'\"*]+)", text[-2000:])
        map_url = urllib.parse.urljoin(js, m.group(1)) if m and not m.group(1).startswith("data:") else js + ".map"
        mst, _, mbody, _ = fetch(map_url, max_bytes=200_000)
        if mst == 200 and b'"sources"' in mbody[:200_000]:
            add("exposure", "source-map", "medium", "Production source map is publicly served", map_url, "",
                "Disable public source maps (e.g. productionBrowserSourceMaps: false in Next.js, build.sourcemap: false or 'hidden' in Vite) or upload them privately to your error tracker.")


def check_exposed_paths(origin: str) -> None:
    # Soft-404 baselines per file extension (SPAs and catch-all routes return 200 for anything).
    baselines: dict[str, str | None] = {}

    def baseline(ext: str) -> str | None:
        if ext not in baselines:
            probe = origin + "/summit-nonexistent-" + hashlib.md5(origin.encode()).hexdigest()[:8] + ext
            st, _, b, _ = fetch(probe, follow=False, max_bytes=50_000)
            baselines[ext] = hashlib.sha1(b[:20000]).hexdigest() if (st == 200 and b) else None
        return baselines[ext]

    for path, kind, sev in EXPOSED_PATHS:
        st, hh, body, _ = fetch(origin + path, follow=False, max_bytes=50_000)
        if st != 200 or not body:
            continue
        ext = os.path.splitext(path)[1]
        if baseline(ext) and hashlib.sha1(body[:20000]).hexdigest() == baseline(ext):
            continue  # soft 404
        ctype = (h1(hh, "content-type") or "").lower()
        if "text/html" in ctype and kind != "binary":
            continue
        text = body.decode("utf-8", errors="ignore")
        if looks_like(kind, text, body):
            add("exposure", "exposed-file", sev, f"Sensitive file is publicly reachable: {path}", origin + path,
                "" if kind == "binary" else text[:120],
                "Remove the file from the published output (or the repo root if the host publishes it), and rotate anything it contained.")
            if kind in ("env", "npmrc", "yaml", "json", "text"):
                scan_text_for_secrets(text, origin + path)

    for d in ("/assets/", "/images/", "/img/", "/uploads/", "/static/", "/files/"):
        st, _, body, _ = fetch(origin + d, follow=False, max_bytes=20_000)
        if st == 200 and body and re.search(rb"<title>\s*Index of /", body[:2000], re.I):
            add("exposure", "directory-listing", "medium", f"Directory listing enabled: {d}", origin + d, "",
                "Disable directory indexes at the host or server.")


def looks_like(kind: str, text: str, raw: bytes = b"") -> bool:
    t = text.lstrip("\ufeff \t\r\n")
    if kind == "binary":
        return raw[:2] == b"PK"
    if t.lower().startswith(("<!doctype", "<html", "<head", "<body")):
        return False
    if kind == "env":
        return bool(re.search(r"^\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=", t, re.M)) or "aws_access_key_id" in t.lower()
    if kind == "git":
        return t.startswith("ref:") or "[core]" in t
    if kind == "npmrc":
        return "registry" in t or "_auth" in t
    if kind == "dsstore":
        return b"Bud1" in raw[:16]
    if kind == "json":
        return t.startswith("{") or t.startswith("[")
    if kind == "yaml":
        return "services:" in t or "version:" in t
    return len(t) > 0


def check_cors(url: str) -> None:
    time.sleep(PAUSE)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Origin": "https://evil.example"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            h = _hdrs(r.headers)
    except urllib.error.HTTPError as e:
        h = _hdrs(e.headers)
    except Exception:
        skip("cors", "request failed")
        return
    acao = h1(h, "access-control-allow-origin") or ""
    acac = (h1(h, "access-control-allow-credentials") or "").lower() == "true"
    if acao == "https://evil.example" and acac:
        add("headers", "cors-reflect", "high", "CORS reflects any Origin with credentials allowed", url, f"ACAO {acao}; ACAC true",
            "Allowlist exact origins and add Vary: Origin. Never reflect the request Origin when credentials are allowed.")
    elif acao == "https://evil.example":
        add("headers", "cors-reflect", "low", "CORS reflects any Origin (no credentials)", url, f"ACAO {acao}",
            "Allowlist exact origins unless the endpoint is intentionally public.")


def check_cert(host: str, port: int = 443) -> None:
    import socket
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
                version = tls.version()
        exp = datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notAfter"]), timezone.utc)
        days = (exp - datetime.now(timezone.utc)).days
        if days < 7:
            add("transport", "cert-expiry", "high", f"TLS certificate expires in {days} days", host, exp.isoformat(),
                "Renew now and check that auto-renewal is working at the host.")
        elif days < 21:
            add("transport", "cert-expiry", "medium", f"TLS certificate expires in {days} days", host, exp.isoformat(),
                "Confirm auto-renewal; most hosts renew 30 days before expiry, so this may mean renewal is failing.")
        if version in ("TLSv1", "TLSv1.1"):
            add("transport", "tls-version", "high", f"Server negotiated {version}", host, "", "Require TLS 1.2 or newer.")
    except ssl.SSLCertVerificationError as e:
        add("transport", "cert-invalid", "high", "TLS certificate does not validate", host, str(e)[:200],
            "Fix the certificate chain or hostname at the host.")
    except Exception as e:
        skip("cert", f"could not connect on {port}: {e}")


def check_security_txt(origin: str) -> None:
    st, _, body, _ = fetch(origin + "/.well-known/security.txt", max_bytes=20_000)
    text = body.decode("utf-8", errors="ignore") if body else ""
    if st != 200 or "contact:" not in text.lower():
        add("disclosure", "security-txt", "info", "No /.well-known/security.txt", origin + "/.well-known/security.txt", "",
            "Publish security.txt with Contact and Expires (RFC 9116). Template in templates/security.txt.",
            ["https://www.rfc-editor.org/rfc/rfc9116"])
        return
    m = re.search(r"^expires:\s*(\S+)", text, re.I | re.M)
    if not m:
        add("disclosure", "security-txt", "low", "security.txt has no Expires field", origin + "/.well-known/security.txt", "", "Add an Expires field (required by RFC 9116).")
    else:
        try:
            exp = datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
            if exp < datetime.now(timezone.utc):
                add("disclosure", "security-txt", "low", "security.txt has expired", origin + "/.well-known/security.txt", m.group(1), "Update the Expires date.")
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# Build output checks
# ---------------------------------------------------------------------------
def check_built(built: Path) -> None:
    if not built.is_dir():
        skip("built", f"{built} is not a directory")
        return
    files = [p for p in built.rglob("*") if p.is_file() and "node_modules" not in p.parts]
    for pattern, sev in FORBIDDEN_PUBLISH_GLOBS:
        for p in built.glob("**/" + pattern):
            if p.is_file() and "node_modules" not in p.parts:
                add("exposure", "publish-forbidden-file", sev, f"File that should not be published is in the build output: {p.relative_to(built)}",
                    str(p.relative_to(built)), "", "Exclude it from the build output (or from the repo root for repo-root publishing).")
    if (built / ".git").exists():
        add("exposure", "publish-git-dir", "high", "Build/publish directory contains a .git folder", ".git", "",
            "Publish a build directory, not the repository root, or block /.git at the host.")
    third_party: dict[str, int] = {}
    inline = 0
    for p in files:
        if p.suffix.lower() not in TEXT_EXT or p.stat().st_size > 8_000_000:
            continue
        try:
            text = p.read_text("utf-8", errors="ignore")
        except Exception:
            continue
        scan_text_for_secrets(text, str(p.relative_to(built)))
        if p.suffix.lower() in (".html", ".htm"):
            ap = AssetParser()
            try:
                ap.feed(text)
            except Exception:
                continue
            inline += ap.inline_scripts
            for s in ap.scripts:
                host = urllib.parse.urlparse(s["src"]).netloc
                if host:
                    third_party[host] = third_party.get(host, 0) + 1
    if third_party:
        add("client-side", "script-inventory", "info", "Third-party script hosts in build output (inventory for CSP and PCI 6.4.3)",
            "build", ", ".join(f"{h} ({n} pages)" for h, n in sorted(third_party.items())),
            "Review each host: is it needed, who owns it, is it in the CSP allowlist.")
    if inline:
        add("client-side", "inline-scripts", "info", f"{inline} inline <script> blocks across built pages", "build", "",
            "Inline scripts need CSP hashes or nonces once CSP is enforced. Prefer external files.")


# ---------------------------------------------------------------------------
# Repository checks
# ---------------------------------------------------------------------------
def check_repo(repo: Path) -> None:
    if not repo.is_dir():
        skip("repo", f"{repo} is not a directory")
        return
    tracked = git_ls(repo)
    if tracked is None:
        skip("repo-git", "not a git repository or git unavailable")
        tracked = [str(p.relative_to(repo)) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts]
    for f in tracked:
        name = os.path.basename(f)
        if re.fullmatch(r"\.env(\.(?!example|sample|template|defaults)[\w.]+)?|\.dev\.vars", name):
            add("secrets", "tracked-env", "high", f"Environment file committed to git: {f}", f, "",
                "Remove it from git (git rm --cached), add to .gitignore, rotate every value it held, and purge history if the repo is or was public.")
        if re.search(r"\.(pem|key|p12|pfx)$", name) or name.startswith("id_rsa"):
            add("secrets", "tracked-key", "critical", f"Key or certificate file committed: {f}", f, "",
                "Remove from git and history, rotate the key.")
    ignored = None
    try:
        r = subprocess.run(["git", "-C", str(repo), "check-ignore", "-q", ".env"], capture_output=True, timeout=15)
        ignored = r.returncode == 0 if r.returncode in (0, 1) else None
    except Exception:
        pass
    if ignored is None:
        gi = repo / ".gitignore"
        ignored = gi.exists() and ".env" in gi.read_text(errors="ignore")
    if not ignored:
        add("secrets", "gitignore-env", "medium", ".gitignore does not exclude .env files", ".gitignore", "",
            "Add .env, .env.* and !.env.example to .gitignore.")

    code_files = [repo / f for f in tracked if Path(f).suffix.lower() in TEXT_EXT | {".env", ".example", ""}]
    for p in code_files:
        if not p.is_file() or p.stat().st_size > 3_000_000 or "node_modules" in p.parts:
            continue
        rel = str(p.relative_to(repo))
        try:
            text = p.read_text("utf-8", errors="ignore")
        except Exception:
            continue
        if not rel.endswith(("package-lock.json", "pnpm-lock.yaml", "yarn.lock")):
            scan_text_for_secrets(text, rel)
        for m in PUBLIC_ENV_RE.finditer(text):
            var = m.group(1)
            rest = var[len(next(px for px in PUBLIC_ENV_PREFIXES if var.startswith(px))):]
            if SECRETISH.search(rest) and not PUBLIC_OK.search(rest):
                add("secrets", "public-env-secret", "high", f"Secret-looking value exposed to the browser: {var}", rel, var,
                    "Variables with public prefixes are bundled into client JavaScript. Rename without the prefix and read it only on the server.")
                break
        if p.suffix in (".tsx", ".jsx", ".js", ".ts", ".astro", ".vue", ".svelte"):
            if "dangerouslySetInnerHTML" in text:
                add("code", "xss-sink", "low", "dangerouslySetInnerHTML used (review that input is trusted or sanitized)", rel, "",
                    "Sanitize with DOMPurify or render as text. Never pass user or CMS input unsanitized.")
            if re.search(r"(?<![\w.])eval\s*\(|new Function\s*\(", text):
                add("code", "eval", "medium", "eval or new Function in source", rel, "", "Remove dynamic code evaluation.")

    check_workflows(repo)
    check_package(repo)


def git_ls(repo: Path) -> list[str] | None:
    try:
        out = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            return None
        return [l for l in out.stdout.splitlines() if l]
    except Exception:
        return None


def check_workflows(repo: Path) -> None:
    wf_dir = repo / ".github" / "workflows"
    if not wf_dir.is_dir():
        skip("workflows", "no .github/workflows")
        return
    for wf in list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")):
        rel = str(wf.relative_to(repo))
        text = wf.read_text(errors="ignore")
        unpinned = []
        for m in re.finditer(r"uses:\s*[\"']?([\w.-]+/[\w./-]+)@([\w.-]+)", text):
            action, ref = m.group(1), m.group(2)
            if action.startswith(("actions/", "github/")):
                continue  # GitHub-owned; pinning still recommended but lower risk
            if not re.fullmatch(r"[0-9a-f]{40}", ref):
                unpinned.append(f"{action}@{ref}")
        if unpinned:
            add("supply-chain", "unpinned-action", "medium", "Third-party GitHub Actions not pinned to a commit SHA", rel,
                ", ".join(sorted(set(unpinned))[:8]),
                "Pin every third-party action to a full commit SHA (tags can be moved by an attacker, as in the 2025 tj-actions/changed-files compromise). Let Dependabot or Renovate update the SHAs.",
                ["https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#using-third-party-actions"])
        if "pull_request_target" in text and re.search(
                r"ref:\s*[\"']?\$\{\{\s*github\.(event\.pull_request\.head|head_ref)|refs/pull/|gh pr checkout", text):
            add("supply-chain", "prt-checkout", "high", "pull_request_target checks out untrusted PR code", rel, "",
                "Do not check out the PR head under pull_request_target; use pull_request, or split into a privileged and an unprivileged workflow.")
        if not re.search(r"^\s*permissions:", text, re.M):
            add("supply-chain", "workflow-permissions", "low", "Workflow does not declare permissions", rel, "",
                "Add a top-level permissions: block (start with contents: read).")
        if run_block_injection(text):
            add("supply-chain", "workflow-injection", "high", "Untrusted event text interpolated into a workflow", rel, "",
                "Pass event text through an env variable instead of ${{ }} inside run: blocks.")


INJECT_RE = re.compile(r"\$\{\{\s*github\.(head_ref|event\.(issue|pull_request|comment|review|review_comment|discussion|"
                       r"discussion_comment|head_commit|workflow_run|pages|commits)\.[\w.\[\]*]*"
                       r"(title|body|message|ref|label|head_branch|name|email|page_name))")


def run_block_injection(text: str) -> bool:
    """True if untrusted event text is interpolated inside a run:/script: block (not env:)."""
    lines = text.splitlines()
    in_block, indent = False, 0
    for line in lines:
        stripped = line.lstrip()
        cur = len(line) - len(stripped)
        m = re.match(r"(-\s*)?(run|script):\s*(.*)$", stripped)
        if m:
            in_block, indent = True, cur
            if INJECT_RE.search(m.group(3)):
                return True
            continue
        if in_block:
            if stripped and cur <= indent:
                in_block = False
            elif INJECT_RE.search(line):
                return True
    return False


def check_package(repo: Path) -> None:
    pkg = repo / "package.json"
    if not pkg.exists():
        return
    locks = [n for n in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock") if (repo / n).exists()]
    if not locks:
        add("supply-chain", "no-lockfile", "medium", "No lockfile committed", "package.json", "",
            "Commit the lockfile and install with npm ci / pnpm install --frozen-lockfile in CI.")
    try:
        data = json.loads(pkg.read_text())
    except Exception:
        return
    for dep_type in ("dependencies", "devDependencies"):
        for name, ver in (data.get(dep_type) or {}).items():
            if isinstance(ver, str) and (ver in ("*", "latest") or ver.startswith(("http:", "git+http:"))):
                add("supply-chain", "loose-version", "medium", f"Dependency {name} uses an unpinned or insecure spec: {ver}", "package.json", "",
                    "Use a semver range from the registry and rely on the lockfile.")


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url")
    ap.add_argument("--built")
    ap.add_argument("--repo")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if not (args.url or args.built or args.repo):
        ap.error("give at least one of --url, --built, --repo")
    started = datetime.now(timezone.utc).isoformat()
    if args.repo:
        check_repo(Path(args.repo).resolve())
    if args.built:
        check_built(Path(args.built).resolve())
    if args.url:
        check_url(args.url)
    out = {
        "tool": "summit-checks", "version": VERSION, "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "targets": {"url": args.url, "built": args.built, "repo": args.repo},
        "findings": FINDINGS, "skipped": SKIPPED,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    counts: dict[str, int] = {}
    for f in FINDINGS:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    print(json.dumps({"out": args.out, "counts": counts, "skipped": len(SKIPPED)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
