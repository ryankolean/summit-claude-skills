#!/usr/bin/env bash
# site-security scan orchestrator.
#
#   scan.sh [--repo DIR] [--built DIR] [--url URL] [--mode audit|gate|monitor]
#           [--profile brochure|app] [--active] [--out DIR]
#
# Runs every installed scanner that applies, records which ran, which were
# skipped and why, normalizes results into findings.json + summary.md, then
# applies the gate policy. A missing, failing or unparseable tool is reported
# as NOT CHECKED, never as clean.
#
# Exit: 0 pass/report-only, 1 blocked, 2 could not verify, 64 usage error.
# Only scan sites you own or have written permission to test.
# Compatible with macOS bash 3.2.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="" BUILT="" URL="" MODE="audit" PROFILE="brochure" ACTIVE=0 OUT=""
TOOL_TIMEOUT="${SITE_SECURITY_TOOL_TIMEOUT:-900}"   # seconds per tool
OBSERVATORY_PKG="@mdn/mdn-http-observatory@1.7.1"   # pinned; bump in the monthly refresh

usage() { sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 64; }
need() { [ $# -ge 2 ] && [ -n "$2" ] || { echo "missing value for $1" >&2; exit 64; }; }
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) need "$@"; REPO="$2"; shift 2 ;;
    --built) need "$@"; BUILT="$2"; shift 2 ;;
    --url) need "$@"; URL="$2"; shift 2 ;;
    --mode) need "$@"; MODE="$2"; shift 2 ;;
    --profile) need "$@"; PROFILE="$2"; shift 2 ;;
    --out) need "$@"; OUT="$2"; shift 2 ;;
    --active) ACTIVE=1; shift ;;
    -h|--help) usage ;;
    *) echo "unknown argument: $1" >&2; usage ;;
  esac
done
[ -z "$REPO$BUILT$URL" ] && usage
case "$MODE" in audit|gate|monitor) ;; *) echo "bad --mode" >&2; exit 64 ;; esac
case "$PROFILE" in brochure|app) ;; *) echo "bad --profile" >&2; exit 64 ;; esac
if [ -n "$REPO" ]; then REPO="$(cd "$REPO" 2>/dev/null && pwd)" || { echo "--repo is not a directory" >&2; exit 64; }; fi
if [ -n "$BUILT" ]; then BUILT="$(cd "$BUILT" 2>/dev/null && pwd)" || { echo "--built is not a directory" >&2; exit 64; }; fi

HOST=""; APEX=""
if [ -n "$URL" ]; then
  case "$URL" in http://*|https://*) ;; *) URL="https://$URL" ;; esac
  HOST="$(printf '%s' "$URL" | sed -E 's#^[a-z]+://##; s#[/:?#].*$##')"
  if ! printf '%s' "$HOST" | grep -Eq '^[A-Za-z0-9][A-Za-z0-9.-]*$'; then
    echo "invalid host in --url: $HOST" >&2; exit 64
  fi
  APEX="${HOST#www.}"
fi

NAME="$(basename "${REPO:-${BUILT:-site}}")"
[ -n "$HOST" ] && [ -z "$REPO" ] && NAME="$HOST"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
STATE="${XDG_STATE_HOME:-$HOME/.local/state}/site-security"
SITE_STATE="$STATE/$NAME"
OUT="${OUT:-$SITE_STATE/$TS}"
if [ -d "$OUT" ] && [ -n "$(ls -A "$OUT" 2>/dev/null)" ]; then
  echo "--out directory is not empty: $OUT" >&2; exit 64
fi
mkdir -p "$OUT/raw" "$OUT/logs"
OUT="$(cd "$OUT" && pwd)"
STATUS="$OUT/status.tsv"; : > "$STATUS"
PREV="$(ls -1d "$SITE_STATE"/2*/ 2>/dev/null | sed 's#/$##' | grep -v "^$OUT\$" | tail -n 1)"

have() { command -v "$1" >/dev/null 2>&1; }
record() { printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" >> "$STATUS"; }
na() { record "$1" "not-applicable" "" "$2"; }
missing() { record "$1" "skipped" "" "not installed: $2"; }
with_timeout() { perl -e 'alarm shift; exec @ARGV or exit 127' "$TOOL_TIMEOUT" "$@"; }

# run NAME OUTFILE file|stdout OKCODES EMPTY_OK CMD...
#   OKCODES: space-separated exit codes that mean "ran"; EMPTY_OK=1 only for tools
#   that legitimately print nothing when clean (trufflehog, nuclei).
run() {
  local name="$1" out="$2" how="$3" ok="$4" empty_ok="$5"; shift 5
  echo "-> $name" >&2
  rm -f "$OUT/raw/$out"
  if [ "$how" = stdout ]; then
    with_timeout "$@" > "$OUT/raw/$out" 2> "$OUT/logs/$name.stderr"
  else
    with_timeout "$@" > "$OUT/logs/$name.stdout" 2> "$OUT/logs/$name.stderr"
  fi
  local rc=$? good=0 c
  for c in $ok; do [ "$rc" = "$c" ] && good=1; done
  if [ "$rc" = 142 ]; then record "$name" failed "$out" "timed out after ${TOOL_TIMEOUT}s"; return 0; fi
  if [ $good != 1 ]; then record "$name" failed "$out" "exit $rc (see logs/$name.stderr)"; return 0; fi
  if [ ! -s "$OUT/raw/$out" ]; then
    if [ "$empty_ok" = 1 ]; then echo "[]" > "$OUT/raw/$out"
    else record "$name" failed "$out" "exit $rc but no output (see logs/$name.stderr)"; return 0; fi
  fi
  record "$name" ran "$out" "exit $rc"
  return 0
}

# Secrets scanners: optionally limit history to the PR range in gate mode.
LOG_RANGE=""
if [ "$MODE" = gate ] && [ -n "${GITHUB_BASE_REF:-}" ]; then LOG_RANGE="origin/$GITHUB_BASE_REF..HEAD"; fi
leaks_git() {  # TOOL
  local tool="$1"; local extra=()
  if [ -n "$LOG_RANGE" ] && "$tool" git --help 2>&1 | grep -q -- "--log-opts"; then extra=(--log-opts="$LOG_RANGE"); fi
  run "$tool" "$tool.json" file "0" 0 "$tool" git --report-format json --report-path "$OUT/raw/$tool.json" \
    --redact --exit-code 0 --no-banner ${extra[@]+"${extra[@]}"} "$REPO"
}

echo "site-security: mode=$MODE profile=$PROFILE out=$OUT" >&2

# ---- built-in checks (always) ---------------------------------------------
args=()
[ -n "$REPO" ] && args+=(--repo "$REPO")
[ -n "$BUILT" ] && args+=(--built "$BUILT")
[ -n "$URL" ] && args+=(--url "$URL")
run summit-checks summit-checks.json file "0" 0 python3 "$HERE/checks.py" ${args[@]+"${args[@]}"} --out "$OUT/raw/summit-checks.json"

if [ -n "$REPO" ]; then
  # ---- secrets ------------------------------------------------------------
  if have betterleaks; then leaks_git betterleaks
  elif have gitleaks; then leaks_git gitleaks
  else missing gitleaks "brew install betterleaks (or gitleaks)"; fi
  if [ "$MODE" != gate ]; then
    if have trufflehog; then run trufflehog trufflehog.json stdout "0" 1 bash -o pipefail -c \
      'trufflehog git "file://$1" --results=verified,unknown --json --no-update | python3 "$2" trufflehog' _ "$REPO" "$HERE/strip_secrets.py"
    else missing trufflehog "brew install trufflehog"; fi
  fi

  # ---- dependencies -------------------------------------------------------
  HAS_LOCK=0
  for f in package-lock.json pnpm-lock.yaml yarn.lock bun.lock bun.lockb requirements.txt poetry.lock uv.lock go.sum Cargo.lock composer.lock Gemfile.lock; do
    [ -f "$REPO/$f" ] && HAS_LOCK=1
  done
  if [ $HAS_LOCK = 0 ]; then
    if [ -f "$REPO/package.json" ]; then
      record osv-scanner failed "" "package.json without a lockfile: dependencies unchecked"
    else
      na osv-scanner "no dependency manifests"; na npm-audit "no dependency manifests"
    fi
  elif have osv-scanner; then
    run osv-scanner osv.json file "0 1" 0 osv-scanner scan source -r --format json --output-file "$OUT/raw/osv.json" "$REPO"
  elif [ -f "$REPO/package-lock.json" ] && have npm; then
    run npm-audit npm-audit.json stdout "0 1" 0 npm audit --json --prefix "$REPO"
  else
    missing osv-scanner "brew install osv-scanner"
  fi

  # ---- static analysis ----------------------------------------------------
  if have semgrep; then
    run semgrep semgrep.json file "0" 0 semgrep scan --config p/default --metrics=off --json --output "$OUT/raw/semgrep.json" --quiet "$REPO"
  else
    missing semgrep "brew install semgrep"
  fi

  # ---- CI workflows -------------------------------------------------------
  if [ -d "$REPO/.github/workflows" ]; then
    if have zizmor; then run zizmor zizmor.json stdout "0" 0 zizmor --offline --no-exit-codes --format json "$REPO"
    else missing zizmor "brew install zizmor"; fi
  else
    na zizmor "no .github/workflows"
  fi

  [ -d "$REPO/supabase" ] && record supabase-advisors skipped "" "manual: run 'supabase db advisors' (CLI 2.81.3+) against the linked project"
fi

# ---- build output: secrets with the full rule set ---------------------------
if [ -n "$BUILT" ]; then
  if have betterleaks; then
    run betterleaks-built betterleaks-built.json file "0" 0 betterleaks dir --report-format json --report-path "$OUT/raw/betterleaks-built.json" --redact --exit-code 0 --no-banner "$BUILT"
  elif have gitleaks; then
    run gitleaks-built gitleaks-built.json file "0" 0 gitleaks dir --report-format json --report-path "$OUT/raw/gitleaks-built.json" --redact --exit-code 0 --no-banner "$BUILT"
  fi
fi

# ---- live site -------------------------------------------------------------
if [ -n "$URL" ]; then
  if have npx; then run observatory observatory.json stdout "0" 0 npx -y "$OBSERVATORY_PKG" "$HOST"
  else missing observatory "install Node.js (npx)"; fi
  if [ "$MODE" != gate ]; then
    TESTSSL=""; have testssl && TESTSSL=testssl; [ -z "$TESTSSL" ] && have testssl.sh && TESTSSL=testssl.sh
    if [ -n "$TESTSSL" ]; then run testssl testssl.json file "0" 0 "$TESTSSL" --quiet --jsonfile "$OUT/raw/testssl.json" "$HOST"
    else missing testssl "brew install testssl"; fi
    if have checkdmarc; then run checkdmarc checkdmarc.json file "0" 0 checkdmarc "$APEX" -o "$OUT/raw/checkdmarc.json"
    else missing checkdmarc "pipx install checkdmarc"; fi
    if have docker && docker info >/dev/null 2>&1; then
      chmod a+rwx "$OUT/raw"
      run zap-baseline zap.json file "0 1 2" 0 docker run --rm -u "$(id -u)" -v "$OUT/raw:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
        zap-baseline.py -t "$URL" -J zap.json -I
    else
      missing zap-baseline "Docker not running"
    fi
    if [ $ACTIVE = 1 ]; then
      if have nuclei; then
        run nuclei nuclei.json file "0" 1 nuclei -u "$URL" -tags exposure,misconfig -severity low,medium,high,critical -rl 10 -ni -duc -omit-raw -silent -jsonl -o "$OUT/raw/nuclei.json"
        if grep -qi "could not connect\|no address found\|connection refused" "$OUT/logs/nuclei.stderr" 2>/dev/null; then
          sed -i.bak '$d' "$STATUS" && rm -f "$STATUS.bak"; record nuclei failed nuclei.json "target unreachable (see logs/nuclei.stderr)"
        fi
      else
        missing nuclei "brew install nuclei"
      fi
    else
      na nuclei "active probing is opt-in (--active)"
    fi
  fi
fi

# ---- policy and suppressions: never from the PR under test -----------------
POL="$HERE/../policy.json"; SUPP=""
if [ -n "$REPO" ]; then
  if [ "$MODE" = gate ] && [ -n "${GITHUB_BASE_REF:-}" ]; then
    git -C "$REPO" show "origin/$GITHUB_BASE_REF:.security/policy.json" > "$OUT/policy.json" 2>/dev/null && POL="$OUT/policy.json"
    git -C "$REPO" show "origin/$GITHUB_BASE_REF:.security/suppressions.json" > "$OUT/suppressions.json" 2>/dev/null && SUPP="$OUT/suppressions.json"
  else
    [ -f "$REPO/.security/policy.json" ] && POL="$REPO/.security/policy.json"
    [ -f "$REPO/.security/suppressions.json" ] && SUPP="$REPO/.security/suppressions.json"
  fi
fi

python3 - "$OUT" "$MODE" "$PROFILE" "$REPO" "$BUILT" "$URL" "$TS" <<'PY'
import json, sys
out, mode, profile, repo, built, url, ts = sys.argv[1:8]
tools = {}
for line in open(f"{out}/status.tsv"):
    name, status, output, reason = (line.rstrip("\n").split("\t") + ["", "", "", ""])[:4]
    tools[name] = {"status": status, "output": output, "reason": reason}
json.dump(tools, open(f"{out}/tools.json", "w"), indent=2)
json.dump({"mode": mode, "profile": profile, "repo": repo, "built": built, "url": url, "started": ts},
          open(f"{out}/meta.json", "w"), indent=2)
PY

nargs=("$OUT" --kev-cache "$STATE/.cache/kev.json")
[ -n "$SUPP" ] && nargs+=(--suppress "$SUPP")
[ -n "$PREV" ] && [ -f "$PREV/findings.json" ] && nargs+=(--previous "$PREV/findings.json")
python3 "$HERE/normalize.py" "${nargs[@]}" >&2 || { echo "normalize failed: results could not be verified" >&2; echo "$OUT"; exit 2; }
python3 "$HERE/gate.py" "$OUT" --policy "$POL" --mode "$MODE" --profile "$PROFILE" >&2
rc=$?
echo "$OUT/summary.md"
exit $rc
