---
name: gh-repo-create
description: >
  Create and initialize a new GitHub repository with sensible defaults using the
  gh CLI. Defaults to private. Sets up README, .gitignore, license, and .claude
  directory structure. Chains naturally into architect-plan-for-dispatch and any
  code-writing skill that needs a repo to target. Activates when the user says
  "create a repo", "new repo", "set up a GitHub repo", "gh-repo-create", or when
  another skill needs a fresh repository to write code into.
---

# gh-repo-create

Establish a new GitHub repository under the `ryankolean` org with production-ready
defaults so that downstream skills (architect-plan-for-dispatch, Dispatch workers,
Claude Code sessions) have a clean, consistent target to write into. Private by
default because Summit and client work should never be accidentally public.

## When to Activate

**Manual triggers:**

- "Create a repo"
- "New repo"
- "Set up a GitHub repo"
- "gh-repo-create"
- "Spin up a repo for this"
- "I need a new repo"

**Auto-detect triggers:**

- `architect-plan-for-dispatch` is about to run and no repo exists yet for the project
- A design document or project scope references a repo that doesn't exist
- User describes a greenfield project and there's no target repo mentioned
- Any skill in the pipeline needs to write code but has no repo to push to

**Do NOT activate when:**

- The target repo already exists (check with `gh repo view` first)
- The user is working within an existing repo
- The user says "I'll create the repo myself"

## Input

The skill needs the following. If not provided, ask one question at a time to fill gaps.

| Parameter | Required | Default | Description |
|---|---|---|---|
| `repo_name` | Yes | — | kebab-case repository name (e.g., `carrot-hire`, `dtst`) |
| `visibility` | No | `private` | `private` or `public` |
| `description` | No | — | One-line repo description for GitHub |
| `license` | No | `MIT` | SPDX license identifier. Use `MIT` for open-source, `NONE` for client/proprietary work |
| `gitignore_template` | No | `Node` | GitHub `.gitignore` template name (e.g., `Node`, `Go`, `Python`, `Rust`) |
| `clone_locally` | No | `true` | Whether to clone the repo after creation |
| `init_branch` | No | `main` | Default branch name |

## Process

### Step 1: Validate Prerequisites

```bash
# Confirm gh is authenticated
gh auth status

# Confirm the repo doesn't already exist
gh repo view ryankolean/<repo_name> 2>/dev/null && echo "REPO EXISTS — aborting" && exit 1
```

If the repo already exists, inform the user and stop. Do not overwrite or re-create.

### Step 2: Create the Repository

```bash
gh repo create ryankolean/<repo_name> \
  --private \                          # or --public if visibility=public
  --description "<description>" \
  --license <license> \
  --gitignore <gitignore_template> \
  --clone
```

**Visibility rule:** Default to `--private`. Only use `--public` if the user
explicitly states the repo should be public. When creating a public repo, confirm
with the user before proceeding: "This will be a public repository visible to
everyone. Confirm?"

### Step 3: Initialize Project Structure

After cloning, set up the standard Summit directory scaffold:

```bash
cd <repo_name>

# Create .claude directory for Dispatch plans and code reports
mkdir -p .claude/dispatch/plans
mkdir -p .claude/dispatch/reports

# Create a minimal README if gh didn't generate one
if [ ! -f README.md ]; then
cat > README.md << 'EOF'
# <Repo Name>

<description>

## Getting Started

TODO

## License

<license>
EOF
fi

# Create CLAUDE.md project instructions file
cat > CLAUDE.md << 'EOF'
# Project Instructions

## Overview

<description>

## Conventions

- Follow existing code patterns and naming conventions
- All environment variables go in .env (never committed)
- Tests live alongside source files or in a dedicated __tests__ / tests directory

## Structure

.claude/
  dispatch/
    plans/       # Dispatch execution plans
    reports/     # Code reports from architect-plan-for-dispatch
EOF

# Commit the scaffold
git add -A
git commit -m "chore: initialize project scaffold"
git push origin main
```

### Step 4: Verify and Report

```bash
# Confirm the repo is live
gh repo view ryankolean/<repo_name> --json name,visibility,url,description
```

Report back to the user with:

- Repository URL: `https://github.com/ryankolean/<repo_name>`
- Visibility: `private`/`public`
- Default branch: `main`
- Scaffold contents: what was created
- Next step suggestion: "Ready for architect-plan-for-dispatch" or "Ready for code"

## Output

A fully initialized GitHub repository with:

```
<repo_name>/
├── .claude/
│   └── dispatch/
│       ├── plans/          # Empty, ready for Dispatch plans
│       └── reports/        # Empty, ready for code reports
├── .gitignore              # From GitHub template
├── CLAUDE.md               # Project instructions for Claude Code / Dispatch
├── LICENSE                 # From selected license
└── README.md               # Minimal project README
```

Plus a confirmation message with the repo URL and suggested next action.

## Rules

- **Always default to private.** Summit client work, internal tools, and anything
  without an explicit "make it public" directive must be private. Public repos
  require explicit user confirmation.
- **Never overwrite an existing repo.** Always check `gh repo view` first. If the
  repo exists, report it and ask the user what they want to do.
- **Always create the `.claude/dispatch` structure.** This is the standard
  scaffold that `architect-plan-for-dispatch` expects. Omitting it forces a later
  task to create it, wasting tokens.
- **Always create `CLAUDE.md`.** Dispatch workers and Claude Code sessions read
  this file for project context. A missing `CLAUDE.md` means every worker starts
  blind.
- **Use `ryankolean` as the default org/owner.** Unless the user specifies a
  different GitHub org or personal account, all repos go under `ryankolean`.
- **kebab-case repo names only.** Reject names with spaces, underscores, or
  camelCase. Suggest a kebab-case alternative if needed.
- **Never commit secrets.** If the project needs environment variables, create a
  `.env.example` with placeholder keys, never a `.env` with real values.
- **Confirm public visibility before creating.** If the user says "public", ask
  once to confirm. This prevents accidental exposure of client work.

## Examples

**Good example:**

> User: "I need a new repo for the Carrot Hire project"

```bash
gh repo view ryankolean/carrot-hire 2>/dev/null  # Check — doesn't exist

gh repo create ryankolean/carrot-hire \
  --private \
  --description "Job coordination app for Carrot Fertility" \
  --license MIT \
  --gitignore Node \
  --clone

cd carrot-hire
mkdir -p .claude/dispatch/plans .claude/dispatch/reports
# ... create README.md, CLAUDE.md ...
git add -A && git commit -m "chore: initialize project scaffold" && git push origin main
```

> Response: "Done — `ryankolean/carrot-hire` is live and private at
> https://github.com/ryankolean/carrot-hire. The `.claude/dispatch` scaffold is in
> place. Ready for `architect-plan-for-dispatch` whenever you are."

**Bad example (what to avoid):**

- Creating a public repo without confirming with the user
- Skipping the `.claude/dispatch` directory scaffold
- Using `gh repo create carrot-hire` without the `ryankolean/` prefix (creates
  under the wrong account)
- Not checking if the repo already exists first

## Cross-Surface Behavior

**In Claude Code (has git + gh access):**

- Execute all commands directly
- Clone the repo into the current working directory or a specified path
- Commit and push the scaffold automatically

**In Claude.ai (no git access):**

- Output the full sequence of commands for the user to run
- Provide the commands as a copyable code block
- Remind the user to run `gh auth status` first if they haven't recently

## Chaining

- `interrogate` → `gh-repo-create`: After scoping a greenfield project, create the repo before planning
- `gh-repo-create` → `architect-plan-for-dispatch`: Repo is created, now analyze it and build the execution plan
- `gh-repo-create` → [any code-writing skill]: Any skill that produces code can target the new repo
- `design-doc-review` → `gh-repo-create` → `architect-plan-for-dispatch`: Full pipeline from design doc to repo to dispatch plan
