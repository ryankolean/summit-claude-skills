#!/usr/bin/env bash
# Regression test: builds a deliberately insecure fixture (repo + build output + local
# server) in a path containing spaces, and asserts that the checks catch each seeded issue,
# avoid known false positives, never write secrets to disk, and never report a broken tool
# as clean. Run after any change to the scripts and during the monthly refresh.
#   bash tests/run-fixture.sh
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)/fixture with spaces"
SRV=""
mkdir -p "$T"
trap '[ -n "$SRV" ] && kill "$SRV" 2>/dev/null; rm -rf "$(dirname "$T")"' EXIT
R="$T/repo"
mkdir -p "$R/.github/workflows" "$R/dist/assets" "$R/src/pages"
cd "$R" || exit 1
git init -q && git config user.email t@example.com && git config user.name fixture
printf '{"name":"fixture","dependencies":{"left-pad":"latest"}}\n' > package.json
printf 'node_modules\n' > .gitignore
printf 'STRIPE=sk_live_%s\nDATABASE_URL=postgres://admin:SuperS3cretPw@db.example.net:5432/app\nSMTP_PASSWORD=hunter2hunter2\n' 51FixtureFixtureFixture00 > .env
printf 'export const k = process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY;\nconst ok = process.env.NEXT_PUBLIC_MAPBOX_TOKEN; const ok2 = process.env.VITE_HELPDESK_URL;\n' > app.jsx
printf -- '---\nconst stripe = "sk_live_%s";\n---\n<div />\n' 51AstroAstroAstroAstro000 > src/pages/index.astro
cat > .github/workflows/ci.yml <<'Y'
on: [pull_request_target]
jobs:
  b:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: {ref: "${{ github.event.pull_request.head.sha }}"}
      - uses: "tj-actions/changed-files@v45"
      - run: echo "${{ github.head_ref }}"
Y
cat > .github/workflows/safe.yml <<'Y'
on: [pull_request]
permissions:
  contents: read
jobs:
  b:
    runs-on: ubuntu-latest
    steps:
      - env:
          TITLE: ${{ github.event.pull_request.title }}
        run: echo "$TITLE"
Y
H=$(printf '{"alg":"HS256"}' | base64 | tr -d '=\n' | tr '/+' '_-')
P=$(printf '{"role":"service_role","iss":"supabase"}' | base64 | tr -d '=\n' | tr '/+' '_-')
printf '<html><head><script src="https://cdn.example.com/lib.js"></script><script src="/assets/app.js"></script></head><body class="sk-loading-spinner-container-wrapper-outer-element"><img src="http://insecure.example.com/x.png"></body></html>' > dist/index.html
printf 'var key="%s.%s.fixturefixturefixturefixture";var aws="AKIAIOSFODNN7EXAMPLE";var pem="-----BEGIN PRIVATE KEY-----";\n//# sourceMappingURL=app.js.map\n' "$H" "$P" > dist/assets/app.js
printf '{"version":3,"sources":["src/app.ts"]}' > dist/assets/app.js.map
printf 'SECRET=1\nDB_PASS=topsecretvalue99\n' > dist/.env
git add -A && git commit -qm fixture
PORT=$(( 20000 + RANDOM % 20000 ))
(cd dist && exec python3 -m http.server "$PORT" >/dev/null 2>&1) & SRV=$!
sleep 1

# Fake tools on PATH: a scanner that "succeeds" with garbage output must be reported as failed.
FAKE="$T/fakebin"; mkdir -p "$FAKE"
printf '#!/bin/sh\necho "this is not json"\nexit 0\n' > "$FAKE/zizmor"; chmod +x "$FAKE/zizmor"

PATH="$FAKE:$PATH" bash "$HERE/scripts/scan.sh" --repo "$R" --built "$R/dist" --url "http://127.0.0.1:$PORT" \
  --mode gate --profile brochure --out "$T/run" >/dev/null 2>"$T/scan.err"
RC=$?
F="$T/run/findings.json"
fail=0
ok() { echo "ok   $1"; }
bad() { echo "FAIL $1"; fail=1; }
[ -f "$F" ] || { echo "FAIL no findings.json"; cat "$T/scan.err"; exit 1; }
has() { python3 -c "import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if any(f['check']==sys.argv[2] and sys.argv[3] in f['location'] for f in d['findings']) else 1)" "$F" "$1" "${2:-}"; }

for c in secret-stripe-live-secret secret-supabase-service-role secret-db-url-credentials tracked-env public-env-secret \
         publish-forbidden-file exposed-file source-map unpinned-action prt-checkout workflow-injection \
         hsts csp clickjacking mixed-content third-party-script no-lockfile loose-version gitignore-env; do
  if has "$c"; then ok "$c"; else bad "$c"; fi
done
has secret-stripe-live-secret index.astro && ok ".astro files scanned" || bad ".astro files scanned"
has workflow-injection safe.yml && bad "env: pattern flagged as injection (false positive)" || ok "env: pattern not flagged"
has secret-openai-key "" && bad "kebab-case class flagged as OpenAI key" || ok "no OpenAI false positive"
has secret-aws-access-key "" && bad "AWS EXAMPLE key flagged" || ok "AWS EXAMPLE key ignored"
has secret-private-key "" && bad "bare PEM header flagged" || ok "bare PEM header ignored"
python3 -c "import json,sys;d=json.load(open(sys.argv[1]));v=[f['location'] for f in d['findings'] if f['check']=='public-env-secret'];sys.exit(1 if any('MAPBOX' in x or 'HELPDESK' in x for x in v) else 0)" "$F" \
  && ok "public env allowlist" || bad "public env allowlist"
python3 -c "import json,sys;d=json.load(open(sys.argv[1]));t=d['tools'].get('zizmor',{});sys.exit(0 if t.get('status')=='failed' else 1)" "$F" \
  && ok "garbage tool output reported as failed" || bad "garbage tool output reported as failed"
[ "$RC" = 1 ] && ok "gate blocked (exit 1)" || bad "gate exit $RC (expected 1)"
grep -q '\[redacted' "$F" && ok "secrets redacted" || bad "secrets not redacted"
for s in 51FixtureFixtureFixture00 SuperS3cretPw hunter2hunter2 topsecretvalue99 51AstroAstroAstroAstro000; do
  if grep -rq "$s" "$T/run"; then bad "plaintext secret '$s' written to the run directory"; fi
done
[ $fail = 0 ] && ok "no plaintext secrets in run directory"
exit $fail
