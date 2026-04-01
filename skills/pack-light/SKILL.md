---
name: pack-light
description: >
  Analyze an application's source code and host hardware to recommend the smallest
  possible packaging strategy. Collects hardware specs via system commands, performs
  full dependency tree and CVE analysis, and produces packaging recommendations with
  generated Dockerfiles, CI/CD pipelines, benchmarking commands, and secret hygiene
  checks. Activates when the user says "pack light", "optimize this app", "shrink
  this", "smallest footprint", "analyze the application", or provides an application
  for deployment optimization.
---

# Pack Light

Analyze an application's codebase and the hardware it will run on, then recommend
the leanest packaging strategy — Docker image, standalone binary, or both. Produces
generated build configs and benchmarking commands so the user can validate results
immediately.

## When to Activate

**Manual triggers:**
- "Pack light"
- "Optimize this app for size"
- "Shrink this" / "make this smaller"
- "Smallest footprint"
- "Analyze the application" / "analyze this app"
- "What's the best way to package this?"
- "Help me containerize this efficiently"

**Auto-detect triggers:**
- User provides an application and asks about deployment or packaging
- User mentions Docker image size being too large
- User is deploying to resource-constrained hardware (Pi, small VPS, edge device)
- User asks "how do I make this run on less?"

## Process

Three sequential phases. Do not skip phases or run them out of order.

---

### Phase 1: Hardware Recon

Collect system specifications to understand the target deployment environment.
This determines what packaging strategies are viable.

#### 1.1 Detect the Current Environment

Run system commands automatically to gather specs. Do not ask permission — just
collect the data.

**macOS detection (default assumption if OS unclear):**
```bash
# OS and architecture
sw_vers 2>/dev/null && uname -m

# CPU
sysctl -n machdep.cpu.brand_string 2>/dev/null
sysctl -n hw.ncpu 2>/dev/null

# Memory (bytes → GB)
sysctl -n hw.memsize 2>/dev/null

# Disk (available space)
df -h / 2>/dev/null | tail -1

# Docker availability
docker info --format '{{.OSType}}/{{.Architecture}}' 2>/dev/null || echo "Docker not available"
docker info --format 'Docker Memory: {{.MemTotal}}' 2>/dev/null
```

**Linux detection:**
```bash
# OS
cat /etc/os-release 2>/dev/null | head -5
uname -m

# CPU
lscpu 2>/dev/null | grep -E "Model name|CPU\(s\)|Architecture"

# Memory
free -h 2>/dev/null | head -2

# Disk
df -h / 2>/dev/null | tail -1

# Docker
docker info --format '{{.OSType}}/{{.Architecture}}' 2>/dev/null || echo "Docker not available"
```

#### 1.2 Ask About Target Environment

After collecting specs, ask the user ONE question:

> "I've collected your current system specs. Is this also the target deployment
> environment, or will this run somewhere else?"

If somewhere else, ask targeted follow-ups to fill in:
- Target OS and architecture (amd64, arm64, armv7)
- Available RAM on the target
- Available disk on the target
- Whether Docker is available on the target
- Any hard constraints (e.g., "must run in under 256MB RAM", "no Docker available")

#### 1.3 Produce the Hardware Profile

Summarize findings in a structured block:

```
HARDWARE PROFILE
────────────────────────────────
Build machine:    [OS] / [arch] / [CPU cores] / [RAM] / [disk free]
Target machine:   [OS] / [arch] / [CPU cores] / [RAM] / [disk free]
Docker available: [yes/no] (build) / [yes/no] (target)
Constraints:      [any hard limits stated by user, or "none"]
────────────────────────────────
```

---

### Phase 2: Code Analysis

Analyze the application source to understand its language, framework, dependency
weight, and runtime characteristics.

#### 2.1 Locate the Source

If the user has not provided source code or a path:

> "I need to see the application source. Can you provide the path to the project
> root, a GitHub repo URL, or upload the source files?"

If the user provides a path or URL, read the project structure.

#### 2.2 Identify Language and Framework

Read project manifest files to detect the stack:

| Signal File | Language / Framework |
|---|---|
| `package.json` | Node.js (check for Express, Fastify, Hono, Next.js, etc.) |
| `package.json` + `bun.lockb` | Bun runtime |
| `deno.json` / `deno.lock` | Deno runtime |
| `pyproject.toml` / `requirements.txt` / `setup.py` | Python (check for Flask, FastAPI, Django) |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml` / `build.gradle` | Java / Kotlin |
| `mix.exs` | Elixir |
| `Gemfile` | Ruby |

If the stack is ambiguous (polyglot repo, no clear entrypoint), ask targeted
follow-ups:

> "This looks like a polyglot repo. Which is the primary application you want
> packaged — the [X] service or the [Y] service?"

#### 2.3 Dependency Tree Analysis

Scan the full dependency tree for weight and optimization opportunities.

**Node.js:**
```bash
# Total node_modules size
du -sh node_modules/ 2>/dev/null

# Count of direct vs transitive deps
jq '.dependencies | length' package.json 2>/dev/null
jq '.devDependencies | length' package.json 2>/dev/null

# Heaviest packages
du -sh node_modules/*/ 2>/dev/null | sort -rh | head -20
```

**Python:**
```bash
# Installed package sizes
pip list --format=columns 2>/dev/null
pip show <heavy-suspects> 2>/dev/null

# Total site-packages size
du -sh $(python -c "import site; print(site.getsitepackages()[0])") 2>/dev/null
```

**Go:**
```bash
# Module dependency count
go list -m all 2>/dev/null | wc -l

# Binary size (if already built)
ls -lh <binary> 2>/dev/null

# Build with size flags
go build -ldflags="-s -w" -o /tmp/test-build . 2>/dev/null && ls -lh /tmp/test-build
```

**Rust:**
```bash
# Dependency count
cargo tree 2>/dev/null | wc -l

# Release binary size
cargo build --release 2>/dev/null && ls -lh target/release/<binary>
```

#### 2.4 Identify Heavy Dependencies

Flag dependencies that contribute disproportionate weight. For each one, note:
- Package name and size
- What it's used for in the codebase (grep for imports)
- Whether a lighter alternative exists

#### 2.5 Analyze Runtime Characteristics

Determine what the application actually needs at runtime:
- Does it need a full OS filesystem, or just a binary + config?
- Does it use native extensions or system libraries (e.g., sharp, canvas, libpq)?
- Does it need a writable filesystem at runtime?
- Does it spawn child processes or shells?
- Does it need TLS certificates or CA bundles?
- Does it bind to network ports?

#### 2.6 Security Scan

Before recommending a base image or dependency set, scan for known vulnerabilities.

**Base image CVE check:**
```bash
# If Docker is available, scan candidate base images
docker scout cves <candidate-base-image> 2>/dev/null || \
  echo "Docker Scout not available — note in report"
```

**Dependency vulnerability check:**
```bash
# Node.js
npm audit --production 2>/dev/null

# Python
pip-audit 2>/dev/null || pip install pip-audit --break-system-packages -q && pip-audit

# Go
govulncheck ./... 2>/dev/null

# Rust
cargo audit 2>/dev/null
```

Flag any critical or high severity CVEs. If a recommended base image has known
CVEs, note it in the report and suggest a patched alternative. Do not recommend
base images with unpatched critical vulnerabilities.

#### 2.7 Detect Existing Packaging

Check if the project already has packaging configuration:
```bash
# Check for existing Dockerfile(s)
find . -name "Dockerfile*" -not -path '*/.git/*' 2>/dev/null

# Check for docker-compose
find . -name "docker-compose*" -not -path '*/.git/*' 2>/dev/null

# Check for .dockerignore
test -f .dockerignore && echo ".dockerignore exists" || echo "No .dockerignore"
```

If an existing Dockerfile is found, read it and store its contents for comparison
in Phase 3. This enables the Comparison Mode output.

#### 2.8 Produce the Code Profile

```
CODE PROFILE
────────────────────────────────
Language:           [language] [version]
Framework:          [framework] [version]
Entrypoint:         [path to main file]
Direct deps:        [count]
Transitive deps:    [count]
Dependency weight:  [total size of deps]
Native extensions:  [list or "none"]
Runtime needs:      [filesystem / network / child processes / etc.]
Top 5 heaviest:     [name: size, name: size, ...]
Known CVEs:         [critical: X, high: X, medium: X, or "clean"]
Existing packaging: [Dockerfile found / none]
────────────────────────────────
```

---

### Phase 3: Recommendation + Deliverables

Combine the hardware profile and code profile to recommend the optimal packaging
strategy.

#### 3.1 Ask for Optimization Weighting and Size Budget

Before recommending, ask:

> "I can optimize for three metrics. How would you weight them?"
>
> 1. **Image/artifact size** (smallest possible output)
> 2. **Startup time** (fastest cold start)
> 3. **Runtime memory** (lowest RAM at steady state)
>
> Options: Balanced (default), or tell me which to prioritize.
>
> "Do you have a target size budget? (e.g., 'under 100MB', 'under 50MB')
> If not, I'll optimize as aggressively as the stack allows."

If the user sets a size budget, track it throughout Phase 3. If the recommended
strategy cannot meet the budget, flag it explicitly in the report with an
explanation of what's preventing it and what tradeoffs would be required to hit it.

#### 3.2 Select Packaging Strategy

Evaluate both Docker and standalone binary options, then recommend the best fit.

**Docker Image Strategy Matrix:**

| Scenario | Base Image Recommendation |
|---|---|
| Node.js, no native deps | `node:{version}-alpine` or distroless |
| Node.js, native deps (sharp, canvas, etc.) | `node:{version}-slim` with explicit lib installs |
| Python, minimal deps | `python:{version}-alpine` or `python:{version}-slim` |
| Python, heavy ML/data deps | `python:{version}-slim` (alpine breaks many wheels) |
| Go | `scratch` or `gcr.io/distroless/static` (static binary) |
| Rust | `scratch` or `gcr.io/distroless/cc` (if libc needed) |

**Standalone Binary Strategy Matrix:**

| Scenario | Approach |
|---|---|
| Go | `CGO_ENABLED=0 go build -ldflags="-s -w"` → static binary |
| Rust | `cargo build --release` + `strip` → static binary |
| Node.js | `pkg`, `bun build --compile`, or `deno compile` |
| Python | `PyInstaller --onefile` or `Nuitka` |

**Decision criteria:**
- If Docker is available on target → prefer Docker (better isolation, reproducibility)
- If target is constrained (<512MB RAM, ARM edge device) → prefer standalone binary
- If app has many native deps → prefer Docker (dependency management)
- If app is pure Go/Rust → prefer standalone binary (smaller, no runtime needed)
- If startup time is critical → prefer standalone binary (no container overhead)

#### 3.3 Generate Build Configuration

Based on the selected strategy, generate production-ready files:

**For Docker:**
Generate a multi-stage Dockerfile following these principles:
1. **Build stage:** Full SDK/toolchain image. Install deps, compile, test.
2. **Production stage:** Minimal base image. Copy only the built artifact and
   runtime dependencies.
3. Use `.dockerignore` to exclude `node_modules/`, `.git/`, `dist/`, test files.
4. Pin base image versions (never use `:latest`).
5. Order layers by change frequency (deps first, source last) for cache efficiency.
6. Run as non-root user.
7. Set `HEALTHCHECK` if the app serves HTTP.

Include a `.dockerignore` file.

**For standalone binary:**
Generate the appropriate build script or Makefile with:
1. Optimized compiler flags (strip symbols, LTO, size optimization)
2. Cross-compilation commands if build and target architectures differ
3. Post-build stripping (UPX compression if appropriate)

#### 3.4 Multi-Architecture Support

Check if the build and target architectures differ, or if the user needs to
deploy to multiple architectures (e.g., amd64 + arm64).

If multi-arch is needed, generate `docker buildx` commands:
```bash
# Create a multi-arch builder (one-time setup)
docker buildx create --name pack-light-builder --use 2>/dev/null

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <image-name>:<tag> \
  --push \
  .
```

If standalone binary, generate cross-compilation commands per-language:
- **Go:** `GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build ...`
- **Rust:** `cross build --target aarch64-unknown-linux-musl --release`
- **Node.js (Bun):** `bun build --compile --target=bun-linux-arm64 ...`

Note: Always specify target platforms explicitly. Never assume the build
machine's architecture matches the deployment target.

#### 3.5 Secret Hygiene Check

Before finalizing any generated Dockerfile or build config, audit it for
credential exposure:

**Check for leaked secrets:**
- No `ENV` directives that set API keys, tokens, passwords, or connection strings
- No `COPY` of `.env`, `.env.local`, `.env.production`, or similar files
- No `ARG` values containing secrets that persist in layer metadata
- No hardcoded credentials in `RUN` commands (e.g., `curl -H "Authorization: ..."`)
- `.dockerignore` explicitly excludes `.env*`, `*.pem`, `*.key`, `.git/`

**Best practices to enforce in generated files:**
- Secrets passed at runtime via `--env-file` or orchestrator (Compose, K8s)
- Build-time secrets use `--mount=type=secret` (BuildKit) instead of `ARG`
- Multi-stage builds ensure build-only credentials do not carry to production stage

If any secret hygiene issues are found in an existing Dockerfile (from Phase 2.7),
flag them as **Critical** findings in the report.

#### 3.6 Runtime Healthcheck Tuning

If the application serves HTTP or exposes a health endpoint, generate a
tailored `HEALTHCHECK` instruction:

1. Scan the source for health/readiness endpoints (common patterns:
   `/health`, `/healthz`, `/ready`, `/ping`, `/api/health`)
2. If found, generate a `HEALTHCHECK` that hits the actual endpoint:
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
     CMD wget --no-verbose --tries=1 --spider http://localhost:<port>/<endpoint> || exit 1
   ```
3. If no health endpoint exists, suggest adding one and generate a minimal
   implementation appropriate to the framework
4. Tune `--start-period` based on the application's expected startup time
   (informed by Phase 2 runtime analysis and the user's optimization weighting)

Prefer `wget --spider` over `curl` in the Dockerfile healthcheck to avoid
adding curl to minimal images. If the base image has neither, use a
language-native check script.

#### 3.7 Comparison Mode

If an existing Dockerfile was found in Phase 2.7, produce a side-by-side
comparison:

```
EXISTING vs OPTIMIZED
────────────────────────────────────────────────────
                    Existing          Optimized
Base image:         [image]           [image]
Stages:             [count]           [count]
Est. image size:    [size]            [size]
Non-root user:      [yes/no]          [yes/no]
.dockerignore:      [yes/no]          [yes/no]
Layer count:        [count]           [count]
Secret hygiene:     [pass/fail]       [pass]
Healthcheck:        [yes/no]          [yes/no]
Multi-arch ready:   [yes/no]          [yes/no]
────────────────────────────────────────────────────
```

Below the comparison table, provide a bulleted list of the specific changes
made and the rationale for each. This lets the user understand exactly what
was improved and why, rather than just receiving a new Dockerfile with no
context on what changed.

#### 3.8 Generate CI/CD Pipeline

Produce a GitHub Actions workflow that builds the optimized image or binary:

```yaml
# .github/workflows/pack-light-build.yml
name: Pack Light Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Docker builds
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          tags: <image-name>:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # Size gate (if budget set)
      - name: Check image size
        run: |
          IMAGE_SIZE=$(docker image inspect <image-name>:${{ github.sha }} \
            --format '{{.Size}}')
          MAX_SIZE=<budget-in-bytes>
          if [ "$IMAGE_SIZE" -gt "$MAX_SIZE" ]; then
            echo "Image size ${IMAGE_SIZE} exceeds budget ${MAX_SIZE}"
            exit 1
          fi
```

Customize the workflow based on:
- **Docker strategy:** Include buildx, multi-platform if needed, cache layers
- **Binary strategy:** Include appropriate toolchain setup, cross-compilation
- **Size budget:** If set, add a size gate step that fails the build if exceeded
- **Security:** Include a `docker scout` or `trivy` scan step if CVEs were
  found in Phase 2.6

#### 3.9 Generate Benchmarking Commands

Produce a set of commands the user can run immediately to validate the result:

```bash
# ── Image / Artifact Size ──
docker images <image-name> --format "{{.Size}}"
# or: ls -lh <binary>

# ── Startup Time ──
time docker run --rm <image-name> --health-check
# or: time ./<binary> --version

# ── Runtime Memory ──
docker stats --no-stream <container-name>
# or: /usr/bin/time -v ./<binary> (Linux)
# or: /usr/bin/time -l ./<binary> (macOS)

# ── Layer Analysis (Docker) ──
docker history <image-name>
# Recommend: dive <image-name> (if dive is installed)

# ── Before vs After Comparison ──
echo "Compare these numbers against your current build."
```

#### 3.10 Produce the Final Report

Write the deliverable in this structure:

```markdown
# Pack Light Report: [Application Name]

**Date:** [today's date]
**Analyst:** Claude (Pack Light)
**Application:** [name] ([language] / [framework])
**Optimization weighting:** [user's stated priorities]
**Size budget:** [target or "none set"]

---

## Hardware Profile

[from Phase 1]

## Code Profile

[from Phase 2, including CVE summary]

---

## Security Findings

[CVE summary from Phase 2.6. Flag any critical/high findings.]
[Secret hygiene issues from Phase 3.5, if any.]

---

## Recommendation: [Docker Multi-Stage / Standalone Binary / Both]

> One paragraph explaining why this strategy is optimal given the hardware
> profile, code profile, and optimization weighting.

### Estimated Footprint

| Metric | Current (est.) | Optimized (est.) | Reduction | Budget |
|---|---|---|---|---|
| Image / artifact size | [X] | [Y] | [Z%] | [pass/fail/n/a] |
| Startup time | [X] | [Y] | [Z%] | — |
| Runtime memory | [X] | [Y] | [Z%] | — |

---

## Comparison with Existing Packaging (if applicable)

[from Phase 3.7 — only include if existing Dockerfile was found]

---

## Generated Files

### Dockerfile (or build script)

[complete, copy-pasteable file]

### .dockerignore (if Docker)

[complete file]

### .github/workflows/pack-light-build.yml

[from Phase 3.8]

---

## Benchmarking Commands

[from Phase 3.9]

---

## Dependency Optimization Opportunities (Optional)

> This section identifies code-level changes that could further reduce
> the footprint. These are suggestions, not requirements.

| Current Package | Size | Lighter Alternative | Estimated Savings | Migration Effort |
|---|---|---|---|---|
| [package] | [size] | [alternative] | [savings] | [low/medium/high] |

[For each suggestion, provide a one-sentence rationale.]

---

## Next Steps

1. [First concrete action]
2. [Second concrete action]
3. [Third concrete action]
```

---

## Rules

1. **Always run hardware recon first.** Never skip to code analysis. The hardware
   profile directly influences which packaging strategies are viable.

2. **Never guess the language or framework.** Read manifest files. If ambiguous,
   ask. Getting the stack wrong invalidates the entire recommendation.

3. **Default to macOS assumptions** when running in a Claude environment where
   system commands return Linux specs but the user hasn't specified their target.
   Ask to confirm.

4. **Pin versions in all generated files.** Never use `:latest`, `*`, or unpinned
   dependencies in Dockerfiles or build configs.

5. **The Dependency Optimization section is always optional.** Present it, but
   frame it as "further opportunities" — not as required changes. The user asked
   for packaging optimization, not a code rewrite.

6. **Every estimate must be labeled as an estimate.** Do not state projected
   image sizes or memory usage as facts. Use "est." or "~" consistently.

7. **Generate complete, copy-pasteable files.** The Dockerfile and build configs
   must work as-is. No `[fill in your ...]` placeholders. Use actual values from
   the code analysis.

8. **Always include benchmarking commands.** The user should be able to validate
   every claim in the report by running the provided commands.

9. **If Docker is not available on the target, do not recommend Docker.** This
   seems obvious, but it's a common failure mode. Check Phase 1 results before
   Phase 3 recommendations.

10. **Respect the user's optimization weighting.** If they said "prioritize
    startup time," don't recommend a strategy that optimizes for size at the
    expense of cold start performance.

11. **Never generate files that bake secrets into image layers.** No `ENV` with
    credentials, no `COPY .env`, no `ARG` with tokens. Secrets go in at runtime.
    If an existing Dockerfile violates this, flag it as Critical.

12. **If a size budget is set, enforce it.** The report must explicitly state
    whether the recommendation meets or exceeds the budget. If it exceeds it,
    explain what's preventing it and what tradeoffs would close the gap.

13. **Always generate a CI/CD workflow.** Every recommendation includes a
    GitHub Actions workflow. The workflow must include cache optimization and
    a size gate step if a budget was set.

14. **Comparison mode is automatic, not optional.** If an existing Dockerfile
    was detected in Phase 2.7, always produce the side-by-side comparison table
    in the report. Do not skip it.

15. **CVE findings do not block recommendations, but must be disclosed.** If
    the security scan finds critical CVEs, note them in the Security Findings
    section and recommend patched alternatives. Do not refuse to produce a
    recommendation because of CVEs — the user needs the information to act.

---

## Examples

### Good Example

**Input:** User provides a Node.js Express API with 47 direct dependencies,
running on a 2GB RAM VPS. Existing Dockerfile uses `node:22` with no
multi-stage build.

**Output:** Multi-stage Dockerfile using `node:22-alpine` build stage →
`gcr.io/distroless/nodejs22-debian12` production stage. `.dockerignore`
excludes test files, docs, and `.git`. Report shows estimated image size
reduction from ~950MB (default `node:22`) to ~130MB. Comparison table shows
the existing Dockerfile runs as root, has no healthcheck, and copies `.env`
into the image (flagged as Critical secret hygiene issue). Security scan finds
2 medium CVEs in dependencies, noted in findings. GitHub Actions workflow
includes buildx with GHA cache and a 200MB size gate. Healthcheck hits
`/api/health` detected in the source. Benchmarking commands include `docker
history`, `docker stats`, and a startup time test. Dependency section notes
that `moment` (4.2MB) could be replaced with `dayjs` (6KB) since only
`format()` and `diff()` are used.

### Bad Example (what to avoid)

**Input:** Same Node.js Express API.

**Bad output:** "Use Alpine and multi-stage builds. Here's a generic Dockerfile
template with `[YOUR_APP_NAME]` placeholders. You should probably also look into
reducing your dependencies."

This fails because:
- Dockerfile has placeholders instead of real values from the code analysis
- No hardware profile was collected
- No dependency tree was actually scanned
- No benchmarking commands
- No estimated footprint comparison
- No security scan or secret hygiene check
- No CI/CD workflow generated
- No comparison with the existing Dockerfile
- Vague advice instead of specific, actionable recommendations

---

## Chaining

- **codebase-review → pack-light:** After a codebase review identifies
  performance or deployment issues, pack-light can optimize the packaging.
- **pack-light → workflow-lock:** If the user packages the same type of
  application repeatedly, lock the pack-light output into a reusable template.
- **decompose → pack-light:** For monorepos or multi-service architectures,
  decompose can break the system into individual services, then pack-light
  optimizes each one.
