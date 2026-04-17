---
name: cli-gh
description: >
  Covers effective use of the GitHub CLI (gh) for managing pull
  requests, issues, releases, Actions workflows, repositories, and raw API
  calls. Activates when the user asks about gh, GitHub CLI, automating GitHub
  workflows, or interacting with GitHub from the terminal.
---

# gh — GitHub CLI

**Repo:** https://github.com/cli/cli

Official GitHub CLI. Manage every GitHub resource — PRs, issues, releases,
Actions runs, repos, and the full REST/GraphQL API — without leaving the
terminal. Composes naturally with jq, fzf, and lazygit.

## When to Activate

**Manual triggers:**
- "How do I use gh?"
- "Create a PR from the terminal"
- "Check CI status in the terminal"
- "Automate GitHub with the CLI"

**Auto-detect triggers:**
- User wants to open/review/merge a pull request from the terminal
- User wants to list or triage issues without opening a browser
- User wants to monitor GitHub Actions runs
- User is scripting GitHub workflows (release automation, issue triage)
- User wants to call the GitHub REST or GraphQL API

## Key Commands

### Authentication
```bash
gh auth login                        # Authenticate (browser or token)
gh auth status                       # Show current auth state
gh auth token                        # Print the active token (for curl/API scripts)
gh auth refresh -s write:packages    # Add an OAuth scope
```

### Pull Requests
```bash
gh pr list                           # List open PRs
gh pr list --state merged            # Merged PRs
gh pr list --author "@me"            # Your PRs
gh pr view 123                       # View PR #123
gh pr view 123 --web                 # Open in browser
gh pr create                         # Interactive PR creation
gh pr create --title "Fix bug" --body "Details" --base main
gh pr checkout 123                   # Check out PR branch locally
gh pr diff 123                       # Show PR diff in terminal
gh pr review 123 --approve           # Approve a PR
gh pr review 123 --request-changes --body "Needs tests"
gh pr merge 123 --squash --delete-branch
gh pr merge 123 --auto --squash      # Merge automatically when CI passes
gh pr close 123
gh pr reopen 123
gh pr ready 123                      # Convert draft → ready for review
gh pr checks 123                     # Show CI check status
```

### Issues
```bash
gh issue list                        # List open issues
gh issue list --label bug            # Filter by label
gh issue list --assignee "@me"
gh issue view 42
gh issue create --title "Bug" --body "Steps to reproduce..."
gh issue create --label bug --assignee octocat
gh issue edit 42 --add-label "priority:high"
gh issue close 42 --comment "Fixed in #123"
gh issue transfer 42 owner/other-repo
```

### GitHub Actions / Runs
```bash
gh run list                          # List recent workflow runs
gh run list --workflow ci.yml        # Filter by workflow file
gh run view 12345                    # View a specific run
gh run view 12345 --log              # Stream logs
gh run view 12345 --log-failed       # Logs for failed steps only
gh run watch 12345                   # Watch run until it completes
gh run rerun 12345                   # Re-run a failed run
gh run rerun 12345 --failed          # Re-run only failed jobs
gh workflow list
gh workflow run deploy.yml           # Trigger a workflow dispatch
gh workflow run deploy.yml --ref feature-branch -f env=staging
```

### Releases
```bash
gh release list
gh release view v1.2.3
gh release create v1.2.3 --title "v1.2.3" --notes "Changelog..."
gh release create v1.2.3 ./dist/binary-linux ./dist/binary-darwin
gh release create v1.2.3 --generate-notes   # Auto-generate notes from PRs
gh release upload v1.2.3 ./dist/app.tar.gz  # Upload additional asset
gh release download v1.2.3                  # Download all assets
gh release delete v1.2.3
```

### Repositories
```bash
gh repo list                         # Your repos
gh repo list org --limit 100
gh repo view owner/repo
gh repo clone owner/repo
gh repo create my-project --public --clone
gh repo fork owner/repo --clone     # Fork and clone
gh repo archive owner/repo
gh repo delete owner/repo           # Requires confirmation
gh repo set-default owner/repo      # Set default repo for current directory
```

### Gists
```bash
gh gist list
gh gist create file.py              # Create public gist
gh gist create file.py --secret
gh gist view <id> --raw
gh gist edit <id>
gh gist clone <id>
```

### Raw API Calls
```bash
# REST API (GET is default)
gh api repos/{owner}/{repo}/topics

# POST/PATCH/DELETE
gh api -X POST repos/{owner}/{repo}/issues \
  -f title="New issue" -f body="Body text"

# Pagination
gh api repos/{owner}/{repo}/issues --paginate

# GraphQL
gh api graphql -f query='
  query($owner:String!, $repo:String!) {
    repository(owner:$owner, name:$repo) {
      stargazerCount
      forkCount
    }
  }
' -f owner=cli -f repo=cli
```

### Search
```bash
gh search repos "language:go stars:>1000"
gh search issues "is:open label:bug assignee:@me"
gh search prs "is:open review-requested:@me"
gh search commits "fix authentication" --repo owner/repo
```

## Advanced Patterns

### --json + jq Piping
```bash
# List PR titles and numbers as JSON, filter with jq
gh pr list --json number,title,author \
  | jq '.[] | "\(.number) \(.author.login): \(.title)"'

# Find all open PRs with failing checks
gh pr list --json number,title,statusCheckRollup \
  | jq '.[] | select(.statusCheckRollup != null) |
         select(.statusCheckRollup[] | .conclusion == "FAILURE") |
         {number, title}'

# Get the URL of the latest release
gh release list --json tagName,publishedAt,url \
  | jq 'sort_by(.publishedAt) | last | .url'

# Summarize workflow run durations
gh run list --json databaseId,displayTitle,createdAt,updatedAt \
  | jq '.[] | {title: .displayTitle, duration: ((.updatedAt | fromdateiso8601) - (.createdAt | fromdateiso8601))}'
```

### Auto-merge + CI Monitoring
```bash
# Open PR and auto-merge when checks pass
gh pr create --title "feat: add caching" --body "" \
  && gh pr merge --auto --squash

# Watch CI for the current branch's PR
gh pr checks --watch

# Re-run failed jobs and watch until done
gh run rerun --failed && gh run watch
```

### GraphQL Queries
```bash
# Get all labels in a repo
gh api graphql -f query='
  query {
    repository(owner:"owner", name:"repo") {
      labels(first:100) {
        nodes { name color }
      }
    }
  }
' | jq '.data.repository.labels.nodes'

# Get PR review decisions
gh api graphql -f query='
  query($pr:Int!) {
    repository(owner:"owner", name:"repo") {
      pullRequest(number:$pr) {
        reviewDecision
        reviews(last:5) {
          nodes { author { login } state }
        }
      }
    }
  }
' -F pr=123 | jq '.data.repository.pullRequest'
```

### Scripting and Automation
```bash
# Label all issues mentioning "crash" as a bug
gh issue list --json number,title --limit 200 \
  | jq -r '.[] | select(.title | test("crash";"i")) | .number' \
  | xargs -I{} gh issue edit {} --add-label bug

# Close stale issues (not updated in 90 days)
gh issue list --json number,updatedAt --limit 500 \
  | jq -r --argjson cutoff $(date -v-90d +%s) \
      '.[] | select((.updatedAt | fromdateiso8601) < $cutoff) | .number' \
  | xargs -I{} gh issue close {}

# Bulk-approve renovate PRs
gh pr list --author app/renovate --json number -q '.[].number' \
  | xargs -I{} gh pr review {} --approve
```

### Environment and Config
```bash
gh config set editor nvim
gh config set git_protocol ssh
gh config set prompt disabled          # Disable interactive prompts in scripts
GH_TOKEN=ghp_xxx gh pr list           # Override token for one command
GH_REPO=owner/repo gh issue list      # Override repo for one command
GH_NO_UPDATE_NOTIFIER=1               # Suppress update nag in CI
```

## Practical Examples

### Daily PR Workflow
```bash
# Create branch, commit, push, open PR, set to auto-merge
git checkout -b feat/my-feature
# ... make changes ...
git add -A && git commit -m "feat: my feature"
git push -u origin feat/my-feature
gh pr create --fill --web             # --fill uses commit message as title/body
gh pr merge --auto --squash
```

### Release Automation
```bash
# Tag, create release with generated notes, upload assets
VERSION=v2.3.0
git tag $VERSION && git push origin $VERSION
gh release create $VERSION \
  --generate-notes \
  --title "$VERSION" \
  dist/*.tar.gz dist/*.zip
```

### Monitor CI Across Repos
```bash
# Watch all failing workflows in an org
for repo in $(gh repo list myorg --json name -q '.[].name'); do
  gh run list --repo myorg/$repo --status failure --json displayTitle,url \
    | jq -r ".[] | \"$repo: \(.displayTitle) \(.url)\""
done
```

### Interactive PR Review with fzf
```bash
# Fuzzy-select a PR and check it out
gh pr list --json number,title \
  | jq -r '.[] | "\(.number)\t\(.title)"' \
  | fzf \
  | awk '{print $1}' \
  | xargs gh pr checkout
```

## Chaining with Other Skills

- **jq (cli-jq):** `--json` output + jq is the core `gh` power combo — filter, reshape, and script any GitHub data
- **fzf (cli-fzf):** Pipe `gh pr list`, `gh issue list`, `gh run list` into fzf for interactive selection workflows
- **lazygit:** Use `gh pr checkout` for PR branches, then lazygit for interactive rebasing before merge
- **httpie / curl:** When gh's API shorthand isn't enough, use `gh auth token` to grab a token for raw HTTP calls
