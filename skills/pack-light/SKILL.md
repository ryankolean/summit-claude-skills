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

Read the root directory and detect:

| Signal | What to read |
|---|---|
| Language | File extensions, shebangs, build tool config |
| Framework | `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Gemfile`, `composer.json` |
| Runtime version | `.nvmrc`, `.python-version`, `.tool-versions`, `Dockerfile` if present |
| Entry point | `main.*`, `index.*`, `app.*`, `cmd/`, `src/main/` |
| Existing Docker config | `Dockerfile`, `docker-compose.yml`, `.dockerignore` |

Never assume. Read the files. If multiple languages are present, flag it.

#### 2.3 Dependency Tree Analysis

Produce a dependency weight report based on language:

**Node.js:**
```bash
# Count total dependencies (direct + transitive)
cat package.json | jq '.dependencies + .devDependencies | keys | length'

# Estimate node_modules size if present
du -sh node_modules 2>/dev/null || echo "node_modules not installed"

# Check for known heavy deps
grep -E "moment|lodash|left-pad|aws-sdk|firebase" package.json
```

**Python:**
```bash
# Count packages
pip list 2>/dev/null | wc -l

# Estimate site-packages size
python3 -c "import site; print(site.getsitepackages())" 2>/dev/null

# Check for heavy deps
grep -iE "tensorflow|torch|scipy|pandas|numpy" requirements*.txt 2>/dev/null
```

**Go:**
```bash
# Count modules
grep "^require" -A 9999 go.mod | grep -c "/"

# Check for CGo (complicates static builds)
grep -r "import \"C\"" . --include="*.go" | head -5
```

**Rust:**
```bash
# Count crate dependencies
grep -c "^[a-zA-Z]" Cargo.lock 2>/dev/null

# Check for heavy build deps
grep -E "openssl|libz|pkg-config" Cargo.toml 2>/dev/null
```

**Java/Kotlin:**
```bash
# Gradle: count dependencies
grep -c "implementation\|compile\|runtimeOnly" build.gradle* 2>/dev/null

# Maven: count dependencies
grep -c "<dependency>" pom.xml 2>/dev/null
```

#### 2.4 Security Scan (CVE Analysis)

Run available security tools automatically. Do not ask permission.

```bash
# Node.js — npm audit
npm audit --json 2>/dev/null | jq '{critical: .metadata.vulnerabilities.critical, high: .metadata.vulnerabilities.high, moderate: .metadata.vulnerabilities.moderate}'

# Python — safety check (if installed)
safety check --json 2>/dev/null | jq '.[].vulnerability_id' | head -20

# Go — govulncheck (if installed)
govulncheck ./... 2>/dev/null | head -30

# General — trivy (if installed, covers all languages + Docker layers)
trivy fs . --severity HIGH,CRITICAL --quiet 2>/dev/null | head -40

# Docker image scan (if Dockerfile exists)
trivy image [image-name] --severity HIGH,CRITICAL 2>/dev/null | head -40
```

Report findings with severity counts. Never suppress or downplay CVE results.

#### 2.5 Build Artifact Analysis

Understand what gets built and shipped:

```bash
# Check if compiled artifacts exist
ls -lh dist/ build/ target/ out/ bin/ 2>/dev/null

# Estimate source size
du -sh . --exclude=node_modules --exclude=.git --exclude=vendor 2>/dev/null

# Check for test/dev files that shouldn't ship
find . -name "*.test.*" -o -name "*.spec.*" -o -name "__tests__" -o -name "test/" | head -20
```

#### 2.6 Runtime Characteristics

Determine what the application needs at runtime:

- **Static or dynamic?** Can it run without a runtime installed (compiled binary) or does it need Node, Python, JVM, etc.?
- **System dependencies?** Does it call native libraries, system tools, or OS-specific APIs?
- **Network services?** Does it listen on ports, make outbound calls, require service discovery?
- **Filesystem access?** Does it read/write to disk at runtime? What paths?
- **Secrets?** Does it read env vars, files, or a secrets manager for credentials?
- **Multi-process?** Does it spawn workers, daemons, or require an init system?

#### 2.7 Existing Docker Analysis (if Dockerfile exists)

If a Dockerfile is present, analyze it:

```
EXISTING DOCKER ANALYSIS
────────────────────────────────
Base image:          [FROM line]
Base image size:     [if known]
Build stages:        [multi-stage or single]
Layer count:         [number of RUN/COPY/ADD instructions]
.dockerignore:       [present/missing]
Non-root user:       [yes/no]
Pinned versions:     [yes/no — in FROM, apt-get, pip install]
Secrets baked in:    [any ENV, ARG, or COPY of .env files?]
Known anti-patterns: [list any found]
────────────────────────────────
```

#### 2.8 Code Analysis Report

Summarize all Phase 2 findings:

```
CODE ANALYSIS REPORT
────────────────────────────────
Language:          [primary language + version]
Framework:         [framework + version]
Entry point:       [file path]
Dep count:         [direct] direct / [transitive] transitive
Dep weight:        [size of node_modules/site-packages/vendor]
Heavy deps:        [list any flagged]
CVEs:              [critical: N | high: N | moderate: N] or "scan not available"
Build output:      [compiled binary / JS bundle / JAR / wheel / etc.]
Source size:       [MB]
Runtime needed:    [Node 18 / Python 3.11 / JVM / none — static binary]
System deps:       [list any: libpq, openssl, ffmpeg, etc. — or "none"]
────────────────────────────────
```

---

### Phase 3: Recommendation + Deliverables

Use the Hardware Profile and Code Analysis Report to recommend the optimal packaging
strategy and generate all required files.

#### 3.1 Strategy Decision Matrix

Score each packaging option against the collected data:

| Strategy | Choose when |
|---|---|
| **Scratch image** | Static binary, zero system deps, minimal attack surface needed |
| **Distroless** | Compiled language, minimal system deps, security-conscious environment |
| **Alpine-based** | Interpreted language, musl-compatible, size is top priority |
| **Slim variant** (`debian-slim`, `ubuntu-minimal`) | Need apt but want small image; glibc required |
| **Full base** (`debian`, `ubuntu`) | Complex system deps, developer ergonomics needed, size not critical |
| **Standalone binary** | Go/Rust/compiled C, no Docker on target, edge/embedded deployment |
| **AppImage / single-file** | Desktop Linux, no Docker, user-space install needed |
| **Hybrid (binary + minimal image)** | Need Docker registry + minimal size |

Apply these rules:
1. If target has no Docker → standalone binary is the only option
2. If `import "C"` or native libs → scratch is probably not viable
3. If Python/Node → Alpine + layer caching is default; warn about musl compat issues
4. If JVM → Distroless Java or GraalVM native image
5. If image size > 1GB and no hard reason → flag and recommend alternatives

#### 3.2 Multi-Strategy Comparison (when multiple options are viable)

Present a comparison table before recommending:

```
STRATEGY COMPARISON
────────────────────────────────────────────────────────
Strategy              Est. Size   Build Time   Complexity   Security
─────────────────────────────────────────────────────────
Scratch (binary)      ~10-30 MB   Med           Low          Highest
Distroless            ~30-50 MB   Med           Low          High
Alpine                ~50-150 MB  Fast          Low          Medium
Debian Slim           ~150-300 MB Fast          Low          Medium
Full Debian           ~500MB+     Fast          Low          Low
────────────────────────────────────────────────────────
Recommendation: [strategy] — [one-sentence reason]
```

#### 3.3 Generate: Dockerfile

Generate a complete, production-ready Dockerfile. Rules:
- Pin ALL versions (base image tag, apt packages, pip/npm/cargo versions)
- Multi-stage build unless the language genuinely doesn't benefit from it
- Non-root user always
- `.dockerignore` companion file always
- No secrets baked in (never `ENV SECRET=...` or `COPY .env .`)
- Minimize layers: chain RUN commands, clean package caches in same layer
- Add `HEALTHCHECK` if the app exposes a port
- Add `LABEL` with maintainer and version

Example structure for a Node.js app:
```dockerfile
# Stage 1: Build
FROM node:20.11.0-alpine3.19 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20.11.0-alpine3.19
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
USER appuser
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

#### 3.4 Generate: .dockerignore

```
.git
.gitignore
node_modules
npm-debug.log
.env
.env.*
*.test.*
*.spec.*
__tests__/
test/
tests/
coverage/
.nyc_output
.DS_Store
*.md
docs/
.github/
```

Adapt for the detected language/framework.

#### 3.5 Generate: CI/CD Workflow

Generate a GitHub Actions workflow (or ask if they use GitLab CI / CircleCI / other):

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix=sha-
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
          format: table
          exit-code: '1'
          severity: CRITICAL,HIGH
```

#### 3.6 Generate: Benchmarking Commands

Produce copy-pasteable commands so the user can validate size and performance:

```bash
# Build the image
docker build -t myapp:pack-light .

# Check final image size
docker image inspect myapp:pack-light --format='{{.Size}}' | numfmt --to=si

# Layer-by-layer size breakdown
docker history myapp:pack-light --no-trunc --format "table {{.CreatedBy}}\t{{.Size}}"

# Run a container and check memory at idle
docker run -d --name myapp-test myapp:pack-light
docker stats myapp-test --no-stream

# Startup time benchmark
time docker run --rm myapp:pack-light [your-exit-command]

# Compare with previous image (if exists)
docker image ls | grep myapp

# For binaries: check static linking
file ./myapp-binary
ldd ./myapp-binary 2>/dev/null || echo "statically linked"

# For binaries: check size
ls -lh ./myapp-binary
```

#### 3.7 Secret Hygiene Check

Scan the repository for secrets before shipping:

```bash
# Check for .env files accidentally committed
git log --all --full-history -- "*.env" | head -5

# Check for hardcoded secrets patterns in source
grep -rE "(password|secret|api_key|token|private_key)\s*=\s*['\"][^'\"]{8,}" \
  --include="*.js" --include="*.py" --include="*.go" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.git . | head -20

# Check current Dockerfile for baked-in secrets
grep -iE "^ENV.*(SECRET|KEY|TOKEN|PASSWORD|PASS)" Dockerfile 2>/dev/null

# Check if .env is in .dockerignore
grep "\.env" .dockerignore 2>/dev/null || echo "WARNING: .env not in .dockerignore"
```

Report any findings. Never proceed to generate files that would bake secrets into images.

#### 3.8 Final Recommendation Summary

Present a structured summary before delivering files:

```
PACK LIGHT RECOMMENDATION
════════════════════════════════════════════════════════
Application:      [name] ([language] [version])
Target hardware:  [arch] / [RAM] / [disk]
Strategy:         [chosen strategy]

Before:           [existing image size or "no Dockerfile"]
After (est.):     [estimated optimized image size]
Reduction:        [% reduction or "N/A — new"]

Files generated:
  ✓ Dockerfile
  ✓ .dockerignore
  ✓ .github/workflows/docker-build.yml
  ✓ Benchmarking commands

CVE status:       [clean / N critical / N high — action required]
Secret hygiene:   [clean / issues found — see above]

Next steps:
  1. [Copy Dockerfile to project root]
  2. [Run benchmark commands to validate]
  3. [Address CVEs if any found]
════════════════════════════════════════════════════════
```

Then deliver all generated files in full, ready to copy-paste.

---

## Rules

1. **Always run hardware recon first.** Never skip Phase 1 — hardware constraints
   determine the viable strategies.

2. **Never guess the language or framework.** Read the files. If ambiguous,
   ask. A wrong assumption produces a Dockerfile that doesn't work.

3. **Pin versions in all generated files.** `FROM node:20.11.0-alpine3.19` not
   `FROM node:alpine`. Unpinned images are a deployment liability.

4. **Generate complete, copy-pasteable files.** No placeholders, no `[TODO]`,
   no `# fill this in`. If you don't have enough info for a field, ask before
   generating.

5. **Always include benchmarking commands.** The user should be able to validate
   the recommendation immediately. Include size and memory commands.

6. **Never generate files that bake secrets into image layers.** If the existing
   code does this, flag it and refuse to replicate the pattern.

7. **Always generate a CI/CD workflow.** A Dockerfile without a pipeline is
   half-deployed. Default to GitHub Actions; ask if they use something else.

8. **CVE findings must be disclosed.** Never suppress or minimize security
   findings. If critical CVEs exist, the recommendation must address them even
   if it changes the packaging strategy.
