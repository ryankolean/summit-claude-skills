# findings.json schema

Produced by `normalize.py`. Stable so the framework's `checks` package and the monthly
report can consume it.

```json
{
  "generated": "ISO-8601",
  "meta": {"mode": "audit|gate|monitor", "profile": "brochure|app", "repo": "", "built": "", "url": "", "started": ""},
  "counts": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0},
  "tools": {"<tool>": {"status": "ran|skipped|failed|not-applicable", "output": "file", "reason": "", "findings": 0}},
  "findings": [{
    "id": "<tool>-<12 hex>",          // stable across runs for the same issue and location
    "tool": "summit-checks|betterleaks|gitleaks|trufflehog|osv-scanner|npm-audit|semgrep|zizmor|observatory|testssl|zap|nuclei|checkdmarc",
    "check": "rule or check id",
    "category": "headers|transport|cookies|exposure|disclosure|client-side|supply-chain|dependency|secrets|code|sast|dast|tls|email-dns|availability",
    "severity": "critical|high|medium|low|info",
    "title": "plain-language summary",
    "location": "file:line, URL, or package",
    "evidence": "redacted, max 300 chars",
    "fix": "how to resolve",
    "references": ["url"],
    "cwe": ["CWE-79"],
    "owasp": "A02:2025 Security Misconfiguration",
    "aliases": ["CVE-..."],            // dependency findings
    "kev": true                        // present when listed in CISA KEV
  }],
  "suppressed": [{"...finding...": "", "suppressed_reason": "", "suppressed_until": "YYYY-MM-DD"}],
  "kev_loaded": true
}
```

## Suppressions (`.security/suppressions.json` in the site repo)
```json
{"suppress": [
  {"check": "csp-weak", "location": "https://example.com", "reason": "Inline script required by Toast embed; nonce migration tracked in SUMMIT-300", "expires": "2026-12-31"},
  {"id": "semgrep-1a2b3c4d5e6f", "reason": "Test fixture, not shipped", "expires": "2027-03-31"}
]}
```
Every suppression needs a reason and an expiry. Expired entries stop applying.
