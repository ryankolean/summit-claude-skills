#!/usr/bin/env bash
# Install or update the site-security scanners on macOS (Homebrew).
# Safe to re-run: upgrades what is already installed.
# Versions verified 2026-10-10; see references/tools.md.
set -u

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required: https://brew.sh" >&2
  exit 1
fi

# Official Homebrew core formulae only. Do not add third-party taps for scanners:
# the aquasecurity tap was compromised in the March 2026 Trivy incident.
FORMULAE="betterleaks trufflehog osv-scanner semgrep zizmor testssl nuclei syft pipx"

for f in $FORMULAE; do
  if brew list --formula "$f" >/dev/null 2>&1; then
    echo "upgrading $f"; brew upgrade "$f" 2>/dev/null || true
  else
    echo "installing $f"
    if ! brew install "$f"; then
      [ "$f" = betterleaks ] && { echo "betterleaks unavailable, falling back to gitleaks"; brew install gitleaks; }
    fi
  fi
done

pipx install checkdmarc 2>/dev/null || pipx upgrade checkdmarc

echo
echo "Optional:"
command -v docker >/dev/null 2>&1 && echo "  docker: found (ZAP baseline enabled)" || echo "  docker: not found. Install Docker Desktop to enable the ZAP baseline scan."
command -v npx >/dev/null 2>&1 && echo "  npx: found (MDN Observatory enabled)" || echo "  npx: not found. Install Node.js to enable the MDN Observatory scan."
command -v supabase >/dev/null 2>&1 && echo "  supabase: $(supabase --version 2>/dev/null) (need 2.81.3+ for 'db advisors')" || echo "  supabase CLI: not found (only needed for Supabase projects: brew install supabase/tap/supabase)"
echo
echo "Installed versions:"
for t in betterleaks gitleaks trufflehog osv-scanner semgrep zizmor testssl nuclei syft checkdmarc; do
  command -v "$t" >/dev/null 2>&1 && printf '  %-12s %s\n' "$t" "$("$t" --version 2>/dev/null | head -n 1)"
done
echo
echo "Semgrep: always pass --metrics=off (scan.sh does). Registry rules are licensed for internal use only."
