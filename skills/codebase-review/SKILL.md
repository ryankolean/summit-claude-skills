---
name: codebase-review
description: >
  Perform a comprehensive senior-architect-level code review of an entire codebase
  after a major update. Evaluates 10 dimensions (data integrity, test coverage,
  security, accessibility, performance, and more), assigns an overall letter grade,
  and produces a prioritized top-10 improvement plan with effort estimates. Activates
  when the user asks for a "code review", "architecture review", "codebase audit",
  "deep dive review", or "review this repo."
---

# Codebase Review

Conduct a thorough senior-architect-level review of a codebase. Evaluate 10 quality
dimensions, assign a letter grade, and deliver a prioritized improvement roadmap with
effort estimates. Designed to run after a major update or before a release milestone.

## When to Activate

**Manual triggers:**
- "Code review" / "review the codebase" / "review this repo"
- "Architecture review" / "architecture audit"
- "Deep dive review"
- "Audit this code"
- "Give me a health check on this codebase"
- "Grade this codebase"

**Auto-detect triggers:**
- User says "we just finished a major refactor — can you take a look?"
- User asks "how is the overall quality of this project?"
- User is preparing for a release or handoff and wants a quality assessment

## Phase 1: Orient (5-8 tool calls)

Read the project's structural foundation before sampling any code.

### 1.1 Project Manifest
Read these files if they exist (prioritize what's present):
- `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` — deps, scripts, metadata
- `tsconfig.json` / `tsconfig.*.json` — TypeScript strictness settings
- `.eslintrc*` / `biome.json` / `.prettierrc` — linting and formatting config
- `jest.config.*` / `vitest.config.*` / `pytest.ini` — test framework and coverage config
- `.env.example` / `docker-compose.yml` / `Dockerfile` — environment and deploy config
- `CLAUDE.md` / `README.md` — documented conventions and onboarding story

### 1.2 Directory Tree
Use a shell command to get a two-level directory tree:
```
find . -maxdepth 2 -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -not -path '*/dist/*' -not -path '*/.next/*' | sort
```
Identify the architectural layers present (e.g., main process, renderer, API,
data layer, UI components, tests, build scripts).

### 1.3 First Impressions
Before reading any code, note:
- What type of project is this? (Electron app, web app, CLI, library, API, etc.)
- What's the rough scale? (file count, apparent complexity)
- What framework/stack is in use?
- Are tests present at all?
- Does a CI/CD pipeline exist?

## Phase 2: Sample the Codebase (15-20 tool calls)

Read representative files from each architectural layer. The goal is breadth,
not depth — you're looking for patterns, not every line.

### Sampling Strategy

**Entry points and orchestration:**
- Main process / app entry (e.g., `src/main.ts`, `main.py`, `cmd/main.go`)
- Root router or controller
- App bootstrap / initialization code

**Data layer:**
- Schema definitions (Zod, Yup, Prisma, SQL, Pydantic, etc.)
- Data access / repository layer
- File I/O or database query code
- Any data parsing or transformation utilities

**Business logic:**
- The most complex service or module (largest file by lines, or most-imported)
- A utility module that is imported broadly
- Any state management (Redux, Zustand, MobX, Context, etc.)

**UI / presentation layer (if applicable):**
- A complex component with meaningful logic
- A form with validation
- Any component that handles user input

**Security surface:**
- IPC handlers (Electron), API routes, WebSocket handlers
- Authentication or session management code
- Any code that touches the filesystem, shell, or network
- Content Security Policy config (if web-facing)

**Tests:**
- One unit test file
- One integration test file (if present)
- One e2e test file (if present)

**Build and deploy:**
- CI/CD config (`.github/workflows/`, `Jenkinsfile`, etc.)
- Build script or bundler config
- Release / packaging config (e.g., `electron-builder.yml`)

Cap total tool calls for reading at **30**. If the codebase is large, prefer
reading more files briefly over reading fewer files completely.

## Phase 3: Evaluate 10 Dimensions

Score each dimension **A through F** using the rubric below.
Be honest — a C is normal for a production codebase under active development.

---

### Dimension 1: Data Integrity & Validation
**What to look for:**
- Are external inputs (user input, file reads, IPC messages, API responses)
  validated before use?
- Is there a schema validation library in use (Zod, Yup, Joi, Pydantic, etc.)?
- Are parse failures handled gracefully (no silent swallowing of errors)?
- Is there protection against data shape mismatches at runtime?

**Grade guide:**
- **A:** Schema validation at all external boundaries; parse errors surface clearly
- **B:** Most boundaries validated; occasional gaps
- **C:** Validation present in some layers; inconsistent
- **D:** Minimal validation; frequent unchecked assumptions
- **F:** No validation; data used as-is from external sources

---

### Dimension 2: Test Coverage & Quality
**What to look for:**
- Is a test framework configured?
- Are tests present and non-trivial?
- Are unit, integration, and e2e tests all represented?
- Is code coverage tracked (even informally)?
- Do tests cover edge cases and failure paths, or only happy paths?

**Grade guide:**
- **A:** Solid unit + integration coverage; e2e for critical flows; coverage >70%
- **B:** Unit tests present; some integration; coverage 40–70%
- **C:** Some tests exist; mostly happy path; coverage 20–40%
- **D:** Minimal tests; mostly smoke tests or empty test files
- **F:** No tests, or tests are broken/skipped entirely

---

### Dimension 3: Security Posture
**What to look for:**
- IPC handlers (Electron): `contextIsolation`, `nodeIntegration` settings;
  preload script scope; `ipcMain`/`ipcRenderer` input validation
- Web apps: CSP headers, XSS vectors, CSRF protection
- Input sanitization: SQL injection, path traversal, shell injection
- Secrets management: hardcoded credentials, env var exposure
- Dependency hygiene: known CVEs in `package-lock.json` / lockfile

**Grade guide:**
- **A:** Defense-in-depth; all IPC/API inputs validated; no known CVEs; CSP present
- **B:** Most surfaces secured; minor gaps; no critical CVEs
- **C:** Basic security practices; some unsanitized inputs or missing CSP
- **D:** Known vectors present; `nodeIntegration: true` without guards; hardcoded secrets
- **F:** Severe vulnerabilities; no input validation; credentials in source

---

### Dimension 4: Error Handling & Resilience
**What to look for:**
- Are async operations wrapped in try/catch or `.catch()`?
- Are errors logged with enough context to debug?
- Does the app degrade gracefully on failure (shows error UI vs. crashes)?
- Is there crash recovery or restart logic?
- Are unhandled promise rejections caught at the process level?

**Grade guide:**
- **A:** Consistent error handling; graceful degradation; errors logged with context
- **B:** Most async paths handled; occasional silent failures
- **C:** Inconsistent; some paths unhandled; errors swallowed in places
- **D:** Try/catch mostly absent; app crashes on common errors
- **F:** No error handling; frequent unhandled rejections

---

### Dimension 5: Code Organization & DRY
**What to look for:**
- Is there a clear separation of concerns (presentation, logic, data)?
- Are shared utilities centralized, or is code copy-pasted across modules?
- Are module boundaries respected?
- Is there obvious dead code or commented-out blocks?
- Is naming consistent and descriptive?

**Grade guide:**
- **A:** Clear layers; DRY utilities; minimal dead code; logical module structure
- **B:** Mostly organized; some duplication; minor boundary leaks
- **C:** Mixed concerns in places; noticeable duplication; some dead code
- **D:** Significant duplication; unclear module responsibilities; large monolithic files
- **F:** No structure; everything in a few files; copy-paste throughout

---

### Dimension 6: Type Safety
**What to look for:**
- Is TypeScript (or equivalent) in use?
- Is `strict: true` enabled in `tsconfig.json`?
- Are `any` types used frequently?
- Are type assertions (`as SomeType`) used to bypass the type system?
- Are runtime type checks present where TypeScript can't verify (e.g., parsed JSON)?

**Grade guide:**
- **A:** `strict: true`; minimal `any`; runtime type validation at boundaries
- **B:** TypeScript in use; some `any` or loose casts; mostly typed
- **C:** TypeScript present but `strict: false`; frequent `any`
- **D:** TypeScript in name only; `any` used broadly; types ignored
- **F:** No type system; or completely unenforced

---

### Dimension 7: Performance & Scalability
**What to look for:**
- Are large lists virtualized (e.g., `react-window`, `@tanstack/virtual`)?
- Are expensive operations debounced or throttled?
- Is data loaded lazily where possible?
- Are there obvious memory leaks (event listeners not cleaned up, intervals not cleared)?
- Are synchronous blocking operations on the main thread?

**Grade guide:**
- **A:** Virtualization for large data; debouncing; lazy loading; no obvious leaks
- **B:** Performance considered; minor gaps; no blocking main-thread operations
- **C:** Functional but no optimization; potential memory leaks; no virtualization
- **D:** Blocking operations; re-renders on every keystroke; obvious leaks
- **F:** Unusable at scale; app hangs under normal load

---

### Dimension 8: Accessibility
**What to look for:**
- Are ARIA attributes used on interactive elements?
- Is keyboard navigation supported (Tab order, focus management)?
- Are form inputs labeled (`<label>`, `aria-label`, `aria-labelledby`)?
- Are color contrast ratios adequate?
- Are screen reader announcements provided for dynamic content?

**Grade guide:**
- **A:** ARIA throughout; full keyboard nav; labels on all inputs; dynamic announcements
- **B:** Most interactive elements accessible; some gaps
- **C:** Basic HTML semantics; minimal ARIA; keyboard nav partially works
- **D:** Custom UI components with no ARIA; keyboard nav broken
- **F:** Completely inaccessible; no semantic markup; mouse-only

---

### Dimension 9: Build & Deploy Pipeline
**What to look for:**
- Is there a CI/CD pipeline (GitHub Actions, CircleCI, etc.)?
- Does the pipeline run tests on every PR/push?
- Is code signing configured for desktop/mobile releases?
- Is there an auto-update mechanism?
- Are build artifacts reproducible and versioned?

**Grade guide:**
- **A:** CI runs tests + lint on every PR; signed releases; auto-update; versioned artifacts
- **B:** CI present; some steps missing (e.g., signing); mostly automated
- **C:** Basic CI; tests not always run; manual release steps
- **D:** No CI; manual build and release process
- **F:** No build pipeline; ad-hoc releases

---

### Dimension 10: Documentation & Onboarding
**What to look for:**
- Does the README explain what the project is, how to install, and how to run?
- Are non-obvious architectural decisions documented (ADRs, inline comments)?
- Is there a `CONTRIBUTING.md` or developer setup guide?
- Are complex functions/modules commented where the logic isn't self-evident?
- Could a new developer be productive within a day?

**Grade guide:**
- **A:** Excellent README; architecture docs; ADRs; meaningful inline comments
- **B:** Good README; some architecture context; partial inline docs
- **C:** Basic README; sparse comments; some setup gaps
- **D:** Minimal README; no inline docs; onboarding requires tribal knowledge
- **F:** No documentation; undiscoverable project

---

## Phase 4: Compute the Overall Grade

Convert letter grades to a GPA-style scale:
- A = 4.0, A- = 3.7
- B+ = 3.3, B = 3.0, B- = 2.7
- C+ = 2.3, C = 2.0, C- = 1.7
- D+ = 1.3, D = 1.0
- F = 0.0

Average the 10 dimension scores. Convert back to a letter grade:
- 3.7–4.0 = A, 3.3–3.6 = A-
- 3.0–3.2 = B+, 2.7–2.9 = B, 2.3–2.6 = B-
- 2.0–2.2 = C+, 1.7–1.9 = C, 1.3–1.6 = C-
- 1.0–1.2 = D+, 0.7–0.9 = D
- Below 0.7 = F

## Phase 5: Prioritized Improvement Plan

Identify the top 10 improvements. Rank by combined **impact × urgency**.

For each item, provide:
- **Priority:** Critical / High / Medium / Low
- **Effort:** X days (be specific — 0.5, 1, 2, 3, 5, 8, 13)
- **Dimension:** Which of the 10 dimensions this addresses
- **What:** One sentence describing the concrete change
- **Why it matters:** One sentence on the consequence of not fixing it

**Prioritization heuristics:**
- Security vulnerabilities → always Critical
- Missing test coverage on core paths → High
- Missing error handling on user-visible paths → High
- Accessibility blockers → High (legal risk + user impact)
- Performance issues under realistic load → High or Medium
- Documentation gaps → Medium (unless blocking onboarding)
- Code style / DRY issues → Low (unless blocking future work)

## Output Format

Write the review in this exact structure:

---

```markdown
# Codebase Review: [Project Name]

**Date:** [today's date]
**Reviewer:** Claude (Senior Architect Mode)
**Project Type:** [Electron app / Web app / CLI / API / Library / etc.]
**Stack:** [primary languages, frameworks, key libraries]

---

## Overall Grade: [LETTER]

> One paragraph executive summary: what this codebase does well, what its
> biggest risks are, and what kind of team/maturity level it reflects.

---

## Dimension Scores

| # | Dimension | Grade | Summary |
|---|-----------|-------|---------|
| 1 | Data Integrity & Validation | [grade] | [one line] |
| 2 | Test Coverage & Quality | [grade] | [one line] |
| 3 | Security Posture | [grade] | [one line] |
| 4 | Error Handling & Resilience | [grade] | [one line] |
| 5 | Code Organization & DRY | [grade] | [one line] |
| 6 | Type Safety | [grade] | [one line] |
| 7 | Performance & Scalability | [grade] | [one line] |
| 8 | Accessibility | [grade] | [one line] |
| 9 | Build & Deploy Pipeline | [grade] | [one line] |
| 10 | Documentation & Onboarding | [grade] | [one line] |

---

## Dimension Deep Dives

### 1. Data Integrity & Validation — [grade]

[2–4 sentences. What you found. Specific file/pattern examples. Concrete gap.]

### 2. Test Coverage & Quality — [grade]

[2–4 sentences...]

[... repeat for all 10 dimensions ...]

---

## Top 10 Improvement Plan

| # | Priority | Effort | Dimension | What | Why It Matters |
|---|----------|--------|-----------|------|----------------|
| 1 | Critical | X days | [dim] | [what] | [why] |
| 2 | High | X days | [dim] | [what] | [why] |
| ... | | | | | |

---

## Appendix: Files Reviewed

- `path/to/file.ts` — [why sampled]
- ...
```

---

## Tone and Standards

- Write as a senior architect doing a genuine peer review, not as a tool running
  a checklist. Use judgment.
- Be specific: name the files, patterns, and line-level examples you found.
- Be honest about grades. A C is not an insult — it is the median production codebase.
- Avoid generic advice. Every recommendation should be actionable with a clear
  next step.
- If a dimension cannot be evaluated due to missing files or context, grade it
  **I** (Incomplete) and explain what information is missing.
- Do not pad the review with praise. Be direct about both strengths and gaps.
