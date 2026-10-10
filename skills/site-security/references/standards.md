# Standards to map findings to

Verified 2026-10-10. `normalize.py` adds a default OWASP Top 10:2025 category per finding
category (editable in its `OWASP` table); adjust per finding during triage.

## Which baseline for which site
- **Brochure / marketing sites:** OWASP Top 10:2025 + ASVS 5.0 Level 1.
- **Apps with auth, personal data or payments:** ASVS 5.0 Level 2 + API Security Top 10
  (2023). Add OWASP LLM Top 10 (2026) and Agentic Top 10 (2026) for AI features.
- **Mobile:** MASVS (STORAGE, CRYPTO, AUTH, NETWORK, PLATFORM, CODE, RESILIENCE, PRIVACY).
- **Payment pages:** PCI DSS 4.0.1 (SAQ A merchants confirm the site is not susceptible to
  script attacks; requirements 6.4.3 / 11.6.1 for others).

## OWASP Top 10:2025
A01 Broken Access Control · A02 Security Misconfiguration · A03 Software Supply Chain
Failures · A04 Cryptographic Failures · A05 Injection · A06 Insecure Design · A07
Authentication Failures · A08 Software or Data Integrity Failures · A09 Security Logging
and Alerting Failures · A10 Mishandling of Exceptional Conditions.
https://top10.owasp.org/2025/

## Default category mapping
| Finding category | OWASP 2025 |
|---|---|
| headers, exposure, disclosure, email-dns | A02 Security Misconfiguration |
| supply-chain, dependency | A03 Software Supply Chain Failures |
| transport, tls, secrets | A04 Cryptographic Failures |
| code (XSS sinks, eval) | A05 Injection |
| cookies | A07 Authentication Failures |
| client-side (third-party scripts, SRI) | A08 Software or Data Integrity Failures |
| Manual: missing auth checks, IDOR, RLS gaps | A01 Broken Access Control |
| Manual: no audit logging or alerting | A09 |

## Others
- ASVS 5.0.0 (May 2025, ~350 requirements in 17 chapters): https://github.com/OWASP/ASVS
- API Security Top 10 2023: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- LLM Top 10 2026 (Aug 2026): https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/
- Agentic Applications Top 10 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- CWE Top 25 (2025): https://cwe.mitre.org/top25/
- MASVS: https://mas.owasp.org/MASVS/
- CISA Secure by Design: https://www.cisa.gov/securebydesign
