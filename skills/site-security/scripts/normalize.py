#!/usr/bin/env python3
"""Merge every scanner's raw output into one findings.json + summary.md.

Usage: normalize.py RUN_DIR [--suppress FILE] [--kev-cache FILE]

RUN_DIR is the directory scan.sh wrote: raw/ holds tool outputs, tools.json
records which tools ran, were skipped (not installed / not applicable) or
failed. Parsers are defensive: a tool whose output cannot be parsed is marked
"failed to parse", never treated as clean.

Python 3.9+ standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import redact  # noqa: E402  single redaction implementation


class ShapeError(ValueError):
    """Tool output did not have the expected structure: treat the tool as failed."""

SEV_ORDER = ["critical", "high", "medium", "low", "info"]
KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

# OWASP Top 10:2025 guidance mapping by category. Editable; see references/standards.md.
OWASP = {
    "headers": "A02:2025 Security Misconfiguration",
    "transport": "A04:2025 Cryptographic Failures",
    "cookies": "A07:2025 Authentication Failures",
    "exposure": "A02:2025 Security Misconfiguration",
    "disclosure": "A02:2025 Security Misconfiguration",
    "client-side": "A08:2025 Software or Data Integrity Failures",
    "supply-chain": "A03:2025 Software Supply Chain Failures",
    "dependency": "A03:2025 Software Supply Chain Failures",
    "secrets": "A04:2025 Cryptographic Failures",
    "code": "A05:2025 Injection",
    "sast": "",
    "dast": "",
    "tls": "A04:2025 Cryptographic Failures",
    "email-dns": "A02:2025 Security Misconfiguration",
    "availability": "",
}


def fid(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:12]


def F(tool, check, category, severity, title, location, evidence="", fix="", refs=None, cwe=None, extra=None):
    sev = severity if severity in SEV_ORDER else "info"
    d = {
        "id": f"{tool}-{fid(tool, check, location, title)}",
        "tool": tool, "check": check, "category": category, "severity": sev,
        "title": title, "location": location, "evidence": redact(evidence or "")[:300],
        "fix": fix, "references": refs or [], "cwe": cwe or [],
        "owasp": OWASP.get(category, ""),
    }
    if extra:
        d.update(extra)
    return d


def load_json(p: Path):
    txt = p.read_text(errors="ignore").strip()
    if not txt:
        return None
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # JSON lines
        out = []
        for line in txt.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        if not out:
            raise ShapeError("output is not JSON")
        return out


def need(cond: bool, what: str) -> None:
    if not cond:
        raise ShapeError(f"unexpected output shape: {what}")


def cvss_to_sev(score) -> str:
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "medium"
    if s >= 9:
        return "critical"
    if s >= 7:
        return "high"
    if s >= 4:
        return "medium"
    return "low" if s > 0 else "info"


# ---------------------------------------------------------------------------
# Parsers: each returns a list of findings
# ---------------------------------------------------------------------------
def p_summit(data):
    need(isinstance(data, dict) and isinstance(data.get("findings"), list), "summit-checks findings list")
    return [dict(f, evidence=redact(f.get("evidence", ""))) for f in data["findings"]]


def p_gitleaks(data, tool="gitleaks"):
    out = []
    need(isinstance(data, list), "gitleaks report array")
    for r in data:
        rule = r.get("RuleID", "secret")
        crit = any(k in rule.lower() for k in ("stripe", "aws", "private-key", "github", "anthropic", "service"))
        loc = f"{r.get('File', '?')}:{r.get('StartLine', '?')}"
        if r.get("Commit"):
            loc += f" (commit {r['Commit'][:8]})"
        out.append(F(tool, f"secret-{rule}", "secrets", "critical" if crit else "high",
                     f"Secret detected: {r.get('Description') or rule}", loc, r.get("Match", "")[:40] + "…",
                     "Rotate the credential first, then remove it from code and history. Load secrets from server-side environment variables."))
    return out


def as_list(data):
    if isinstance(data, dict):
        return [data]
    return data or []


def p_trufflehog(data):
    out = []
    for r in as_list(data):
        if not isinstance(r, dict) or "DetectorName" not in r:
            continue
        meta = (r.get("SourceMetadata") or {}).get("Data") or {}
        src = next(iter(meta.values()), {}) if meta else {}
        loc = f"{src.get('file', '?')}:{src.get('line', '?')}"
        verified = r.get("Verified")
        out.append(F("trufflehog", f"secret-{r['DetectorName']}", "secrets", "critical" if verified else "high",
                     f"{'Verified live' if verified else 'Possible'} {r['DetectorName']} credential", loc, "",
                     "Rotate the credential now (TruffleHog confirmed it works)." if verified else
                     "Confirm whether the credential is real; rotate if so.",
                     extra={"verified": bool(verified)}))
    return out


def p_osv(data):
    out = []
    need(isinstance(data, dict) and "results" in data, "osv results")
    for res in data.get("results", []):
        src = (res.get("source") or {}).get("path", "lockfile")
        for pkg in res.get("packages", []):
            p = pkg.get("package", {})
            name, ver = p.get("name", "?"), p.get("version", "?")
            groups = pkg.get("groups") or []
            vulns = {v.get("id"): v for v in pkg.get("vulnerabilities", [])}
            seen = set()
            for g in groups or [{"ids": list(vulns)}]:
                ids = g.get("ids") or []
                if not ids:
                    continue
                primary = vulns.get(ids[0], {})
                sev = cvss_to_sev(g.get("max_severity")) if g.get("max_severity") else \
                    ((primary.get("database_specific") or {}).get("severity") or "medium").lower()
                sev = {"moderate": "medium"}.get(sev, sev)
                aliases = sorted(set(ids) | set(g.get("aliases") or []) | set(primary.get("aliases") or []))
                key = ids[0]
                if key in seen:
                    continue
                seen.add(key)
                out.append(F("osv-scanner", key, "dependency", sev,
                             f"{name}@{ver}: {primary.get('summary') or key}", f"{src} ({p.get('ecosystem', '')})",
                             ", ".join(aliases)[:200],
                             f"Upgrade {name} to a fixed version (see advisory). Try `osv-scanner fix` or update the direct dependency that pulls it in.",
                             [f"https://osv.dev/vulnerability/{key}"], extra={"aliases": aliases, "package": name}))
    return out


def p_npm_audit(data):
    out = []
    need(isinstance(data, dict), "npm audit object")
    if "error" in data:
        raise ShapeError(f"npm audit error: {str(data['error'])[:120]}")
    need("vulnerabilities" in data or "auditReportVersion" in data, "npm audit report")
    for name, v in (data.get("vulnerabilities") or {}).items():
        sev = {"moderate": "medium"}.get(v.get("severity", "low"), v.get("severity", "low"))
        via = [x.get("title") for x in v.get("via", []) if isinstance(x, dict)]
        urls = [x.get("url") for x in v.get("via", []) if isinstance(x, dict) and x.get("url")]
        fix = v.get("fixAvailable")
        out.append(F("npm-audit", f"npm-{name}", "dependency", sev, f"{name} ({v.get('range', '')}): {via[0] if via else 'see advisory'}",
                     "package-lock.json", "", "Fix available: run npm audit fix, or update the parent package." if fix else
                     "No automatic fix: check the advisory for a workaround or replace the package.", urls[:3]))
    return out


def p_semgrep(data):
    out = []
    need(isinstance(data, dict) and "results" in data, "semgrep results")
    if data.get("errors"):
        fatal = [e for e in data["errors"] if str(e.get("level", "")).lower() == "error" and e.get("type") not in ("Syntax error", "PartialParsing")]
        if fatal and not data["results"]:
            raise ShapeError(f"semgrep errors: {str(fatal[0].get('message', ''))[:120]}")
    m = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}
    for r in data.get("results", []):
        ex = r.get("extra", {})
        meta = ex.get("metadata", {})
        cwe = meta.get("cwe") or []
        cwe = cwe if isinstance(cwe, list) else [cwe]
        conf = (meta.get("confidence") or "").upper()
        sev = m.get(ex.get("severity", "INFO"), "low")
        if conf == "LOW" and sev in ("high", "medium"):
            sev = {"high": "medium", "medium": "low"}[sev]
        out.append(F("semgrep", r.get("check_id", "rule"), "sast", sev, ex.get("message", "")[:160],
                     f"{r.get('path')}:{(r.get('start') or {}).get('line')}", (ex.get("lines") or "")[:200],
                     meta.get("fix", "") or "Review the flagged code; see the rule reference.",
                     meta.get("references", [])[:3] if isinstance(meta.get("references"), list) else [], cwe,
                     extra={"confidence": conf.lower() or None}))
    return out


def p_zizmor(data):
    out = []
    need(isinstance(data, list), "zizmor findings array")
    m = {"informational": "info", "low": "low", "medium": "medium", "high": "high", "unknown": "low"}
    for r in data or []:
        if not isinstance(r, dict):
            continue
        det = r.get("determinations") or {}
        sev = m.get(str(det.get("severity", "low")).lower(), "low")
        locs = r.get("locations") or []
        loc = "workflow"
        if locs:
            try:
                sym = locs[0].get("symbolic", {})
                key = sym.get("key", {})
                if isinstance(key, dict):
                    inner = next(iter(key.values()), {})
                    loc = inner.get("given_path") or inner.get("prefix") or json.dumps(key)[:120] if isinstance(inner, dict) else str(inner)
                else:
                    loc = str(key)
                ann = sym.get("annotation")
                if ann:
                    loc += f" ({ann})"
            except Exception:
                pass
        out.append(F("zizmor", r.get("ident", "workflow"), "supply-chain", sev, r.get("desc", r.get("ident", "")),
                     loc, "", "See the zizmor audit docs for this rule.", [r.get("url")] if r.get("url") else []))
    return out


def p_observatory(data):
    out = []
    need(isinstance(data, dict) and isinstance(data.get("scan"), dict) and "grade" in data["scan"], "observatory scan.grade")
    scan = data.get("scan", {})
    if scan:
        out.append(F("observatory", "grade", "headers", "info", f"MDN HTTP Observatory grade {scan.get('grade')} ({scan.get('score')}/100)",
                     "live site", "", "Use the header templates in templates/headers/ for this host.",
                     ["https://developer.mozilla.org/en-US/observatory"]))
    for name, t in (data.get("tests") or {}).items():
        if t.get("pass") is False:
            mod = t.get("scoreModifier") or 0
            out.append(F("observatory", name, "headers", "medium" if mod <= -20 else "low",
                         f"Observatory test failed: {name} ({t.get('result')})", "live site",
                         str(t.get("scoreDescription", ""))[:200], str(t.get("recommendation", ""))[:300]))
    return out


def p_testssl(data):
    out = []
    need(isinstance(data, (list, dict)) and data, "testssl results")
    m = {"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low", "WARN": "low"}
    items = data.get("scanResult", data) if isinstance(data, dict) else data
    if isinstance(items, list) and items and isinstance(items[0], dict) and "id" not in items[0]:
        flat = []
        for blk in items:
            for v in blk.values():
                if isinstance(v, list):
                    flat.extend(x for x in v if isinstance(x, dict))
        items = flat
    for r in items or []:
        sev = m.get(str(r.get("severity", "")).upper())
        if not sev:
            continue
        out.append(F("testssl", r.get("id", "tls"), "tls", sev, f"TLS: {r.get('id')}: {r.get('finding', '')[:120]}",
                     f"{r.get('ip', '')}:{r.get('port', '')}", "", "Fix at the host or CDN TLS settings.", cwe=[r.get("cwe")] if r.get("cwe") else []))
    return out


def p_zap(data):
    out = []
    need(isinstance(data, dict) and "site" in data, "zap site list")
    m = {"3": "high", "2": "medium", "1": "low", "0": "info"}
    for site in data.get("site", []):
        for a in site.get("alerts", []):
            inst = a.get("instances") or [{}]
            out.append(F("zap", f"zap-{a.get('pluginid')}", "dast", m.get(str(a.get("riskcode")), "low"), a.get("alert") or a.get("name", ""),
                         inst[0].get("uri", site.get("@name", "")), f"{len(inst)} instance(s)",
                         _strip(a.get("solution", ""))[:300], [], [f"CWE-{a.get('cweid')}"] if a.get("cweid") not in (None, "", "-1") else []))
    return out


def _strip(html_text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", html_text or "").strip()


def p_nuclei(data):
    out = []
    for r in as_list(data):
        if not isinstance(r, dict):
            continue
        info = r.get("info", {})
        out.append(F("nuclei", r.get("template-id", "template"), "dast", str(info.get("severity", "info")).lower(),
                     info.get("name", r.get("template-id", "")), r.get("matched-at", r.get("host", "")),
                     "", str(info.get("remediation", "")) or "Review the matched URL and the template description.",
                     (info.get("reference") or [])[:3] if isinstance(info.get("reference"), list) else []))
    return out


def p_checkdmarc(data):
    out = []
    rows = data if isinstance(data, list) else [data]
    need(any(isinstance(d, dict) and ("spf" in d or "dmarc" in d) for d in rows), "checkdmarc spf/dmarc")
    for d in rows:
        if not isinstance(d, dict):
            continue
        dom = d.get("domain", "domain")
        spf = d.get("spf") or {}
        dmarc = d.get("dmarc") or {}
        if not spf.get("valid", False):
            out.append(F("checkdmarc", "spf", "email-dns", "medium", f"SPF record missing or invalid for {dom}", dom, str(spf.get("error", ""))[:200],
                         "Publish one valid SPF TXT record listing every service that sends mail for the domain, ending in -all or ~all."))
        if not dmarc.get("valid", False):
            out.append(F("checkdmarc", "dmarc", "email-dns", "medium", f"DMARC record missing or invalid for {dom}", dom, str(dmarc.get("error", ""))[:200],
                         "Publish _dmarc TXT with p=none and a rua address, review reports, then move to quarantine or reject."))
        else:
            p = (((dmarc.get("tags") or {}).get("p") or {}).get("value") or "").lower()
            if p == "none":
                out.append(F("checkdmarc", "dmarc-policy", "email-dns", "low", f"DMARC policy is p=none for {dom} (monitoring only)", dom, "",
                             "After reviewing DMARC reports, move to p=quarantine, then p=reject, so others cannot send mail as this domain."))
    return out


PARSERS = {
    "summit-checks": p_summit, "gitleaks": p_gitleaks, "betterleaks": lambda d: p_gitleaks(d, "betterleaks"),
    "gitleaks-built": p_gitleaks, "betterleaks-built": lambda d: p_gitleaks(d, "betterleaks"), "trufflehog": p_trufflehog, "osv-scanner": p_osv, "npm-audit": p_npm_audit,
    "semgrep": p_semgrep, "zizmor": p_zizmor, "observatory": p_observatory, "testssl": p_testssl,
    "zap-baseline": p_zap, "nuclei": p_nuclei, "checkdmarc": p_checkdmarc,
}


# ---------------------------------------------------------------------------
def load_kev(cache: Path | None) -> set[str]:
    try:
        if cache and cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 86400:
            data = json.loads(cache.read_text())
        else:
            req = urllib.request.Request(KEV_URL, headers={"User-Agent": "summit-site-security"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
            if cache:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps(data))
        return {v.get("cveID") for v in data.get("vulnerabilities", [])}
    except Exception:
        return set()


def load_suppressions(path: Path | None) -> list[dict]:
    if not path or not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data.get("suppress", []) if isinstance(data, dict) else data
    except Exception:
        print(f"warning: could not parse {path}", file=sys.stderr)
        return []


def apply_suppressions(findings, rules):
    today = date.today().isoformat()
    kept, suppressed = [], []
    valid = []
    for r in rules:
        try:
            ok = bool(r.get("reason")) and date.fromisoformat(str(r.get("expires"))) >= date.today()
        except (TypeError, ValueError):
            ok = False
        if ok and (r.get("id") or (r.get("check") and r.get("location"))):
            valid.append(r)
        else:
            print(f"warning: ignoring suppression without reason, valid future expiry, and id or check+location: {r}", file=sys.stderr)
    rules = valid
    for f in findings:
        hit = None
        for r in rules:
            if r.get("id") and r["id"] == f["id"]:
                hit = r
            elif r.get("check") and r["check"] == f["check"] and r["location"] in f["location"]:
                hit = r
            if hit:
                break
        if hit:
            f = dict(f, suppressed_reason=hit.get("reason", ""), suppressed_until=hit.get("expires"))
            suppressed.append(f)
        else:
            kept.append(f)
    return kept, suppressed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--suppress")
    ap.add_argument("--kev-cache")
    ap.add_argument("--previous", help="findings.json from the previous run of the same site")
    a = ap.parse_args()
    run = Path(a.run_dir)
    tools = json.loads((run / "tools.json").read_text()) if (run / "tools.json").exists() else {}
    checks_skipped = []
    findings = []
    for name, meta in tools.items():
        if meta.get("status") != "ran":
            continue
        raw = run / "raw" / meta.get("output", "")
        parser = PARSERS.get(name)
        if not parser or not raw.exists():
            meta["status"] = "failed"
            meta["reason"] = "no output file produced"
            continue
        try:
            data = load_json(raw)
            got = parser(data)
            if name == "summit-checks":
                checks_skipped = data.get("skipped", [])
            meta["findings"] = len(got)
            findings.extend(got)
        except Exception as e:  # never silently clean
            meta["status"] = "failed"
            meta["reason"] = f"could not parse output: {e}"

    # Dedupe by id
    uniq = {}
    for f in findings:
        uniq.setdefault(f["id"], f)
    findings = list(uniq.values())

    kev = load_kev(Path(a.kev_cache) if a.kev_cache else None)
    if kev:
        for f in findings:
            if any(x in kev for x in f.get("aliases", [])):
                f["severity"] = "critical"
                f["kev"] = True
                f["title"] = "[Known exploited] " + f["title"]

    findings, suppressed = apply_suppressions(findings, load_suppressions(Path(a.suppress) if a.suppress else None))
    resolved = []
    if a.previous and Path(a.previous).exists():
        try:
            prev = json.loads(Path(a.previous).read_text())
            prev_ids = {f["id"] for f in prev.get("findings", [])}
            cur_ids = {f["id"] for f in findings}
            for f in findings:
                f["new"] = f["id"] not in prev_ids
            ran_now = {n for n, t in tools.items() if t.get("status") == "ran"}
            resolved = [f for f in prev.get("findings", []) if f["id"] not in cur_ids and f["tool"] in ran_now | {"summit-checks"}]
        except Exception as e:
            print(f"warning: could not read previous findings: {e}", file=sys.stderr)
    findings.sort(key=lambda f: (SEV_ORDER.index(f["severity"]), f["tool"], f["location"]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEV_ORDER}
    out = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "meta": json.loads((run / "meta.json").read_text()) if (run / "meta.json").exists() else {},
        "counts": counts, "tools": tools, "findings": findings, "suppressed": suppressed,
        "kev_loaded": bool(kev),
        "previous": a.previous, "resolved_since_previous": resolved,
        "checks_skipped": checks_skipped,
    }
    (run / "findings.json").write_text(json.dumps(out, indent=2))
    (run / "tools.json").write_text(json.dumps(tools, indent=2))
    write_summary(run, out)
    print(json.dumps({"findings": str(run / "findings.json"), "counts": counts, "suppressed": len(suppressed)}))
    return 0


def write_summary(run: Path, out: dict) -> None:
    m = out["meta"]
    lines = [f"# Security scan summary", "",
             f"Mode: {m.get('mode', '?')} | Profile: {m.get('profile', '?')} | Started: {m.get('started', '?')}",
             f"Targets: repo={m.get('repo') or '-'} built={m.get('built') or '-'} url={m.get('url') or '-'}", "",
             "## Counts", "", "| Critical | High | Medium | Low | Info | Suppressed |", "|---|---|---|---|---|---|",
             "| " + " | ".join(str(out["counts"][s]) for s in SEV_ORDER) + f" | {len(out['suppressed'])} |", "",
             "## Tool coverage", "", "Anything not marked ran was NOT checked. Do not read a skipped tool as a pass.", "",
             "| Tool | Status | Findings | Note |", "|---|---|---|---|"]
    for name, t in sorted(out["tools"].items()):
        lines.append(f"| {name} | {t.get('status')} | {t.get('findings', '-')} | {t.get('reason', '')} |")
    if out.get("checks_skipped"):
        lines += ["", "Built-in checks not performed:", ""]
        lines += [f"- {c.get('check')}: {c.get('reason')}" for c in out["checks_skipped"]]
    lines += ["", f"KEV enrichment: {'on' if out['kev_loaded'] else 'unavailable (offline?)'}"]
    if out.get("previous"):
        new_n = sum(1 for f in out["findings"] if f.get("new"))
        lines += [f"Compared with previous run: {new_n} new, {len(out.get('resolved_since_previous', []))} resolved."]
    lines += ["", "## Findings (critical to medium)", ""]
    shown = [f for f in out["findings"] if f["severity"] in ("critical", "high", "medium")]
    if not shown:
        lines.append("None at medium or above among the tools that ran.")
    for f in shown[:60]:
        tag = " (NEW)" if f.get("new") else ""
        lines.append(f"- **{f['severity'].upper()}**{tag} [{f['tool']}] {f['title']} at `{f['location']}`")
        if f.get("fix"):
            lines.append(f"  - Fix: {f['fix']}")
    if len(shown) > 60:
        lines.append(f"- ...and {len(shown) - 60} more in findings.json")
    (run / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
