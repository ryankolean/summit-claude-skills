---
name: cli-lazygit
description: >
  Teach Claude how to effectively use lazygit for terminal UI git operations
  including staging, committing, pushing, branching, interactive rebase, merge
  conflict resolution, cherry-pick, bisect, and worktrees. Activates when the
  user asks about lazygit, TUI git workflows, or interactive git operations.
---

# lazygit — Terminal UI for Git

**Repo:** https://github.com/jesseduffield/lazygit

Full-featured terminal UI for git. Navigate your repo, stage changes, commit,
push/pull, manage branches, resolve conflicts, and run interactive rebases —
all without leaving the terminal.

## When to Activate

**Manual triggers:**
- "How do I use lazygit?"
- "Interactive git TUI"
- "Stage individual lines in the terminal"
- "Interactive rebase without memorizing flags"

**Auto-detect triggers:**
- User wants to stage hunks or individual lines interactively
- User wants to resolve merge conflicts in the terminal
- User wants to cherry-pick commits across branches
- User wants to run interactive rebase with a visual UI
- User wants to bisect or manage worktrees interactively

## Key Bindings

### Navigation (Global)
```
hjkl / arrow keys    Navigate panels and lists
[  ]                 Switch between panels (left/right)
<tab>                Cycle focus between panels
q                    Quit lazygit
?                    Show keybinding help for current panel
:                    Run a custom git command
```

### Files Panel
```
space                Stage / unstage file
a                    Stage all / unstage all
c                    Commit staged changes
A                    Amend last commit
e                    Open file in editor
d                    Discard file changes
Enter                Expand file to view diff / stage by hunk
```

### Staging by Hunk or Line
```
# In expanded diff view (press Enter on a file):
space                Stage / unstage hunk
v                    Toggle line selection mode
space (line mode)    Stage / unstage selected lines
=                    Increase context lines
-                    Decrease context lines
```

### Commits Panel
```
Enter                View commit diff
r                    Rename/reword commit message
R                    Reword with editor
d                    Drop commit
s                    Squash into parent
f                    Fixup into parent
e                    Edit commit (interactive rebase stop)
p                    Pick commit
t                    Revert commit
c                    Copy commit (cherry-pick)
C                    Copy commit range (cherry-pick)
v                    Paste (apply cherry-picks)
i                    Start interactive rebase from this commit
```

### Branches Panel
```
b                    Open branches panel
space                Checkout branch
n                    New branch
d                    Delete branch
r                    Rebase current branch onto selected
M                    Merge selected branch into current
f                    Fast-forward branch
Enter                View commits on branch
```

### Stash Panel
```
s                    Stash changes (all)
S                    Stash options (staged, untracked, etc.)
space                Apply stash
g                    Pop stash
d                    Drop stash
```

### Sync (Push/Pull)
```
p                    Pull (current branch)
P                    Push (current branch)
f                    Fetch all remotes
```

## Advanced Patterns

### Interactive Rebase
```bash
# In Commits panel: position cursor on the oldest commit you want to rebase
# Press i — opens interactive rebase mode
# Use e to edit, s to squash, f to fixup, d to drop, r to reword
# Changes are applied as you move through the rebase
```

### Merge Conflict Resolution
```bash
# When a conflict exists, lazygit shows conflict markers in the diff panel
# Navigate to the conflicted file — press Enter to expand
# Use:
#   1  — pick "ours" (current branch)
#   2  — pick "theirs" (incoming)
#   3  — pick both
#   e  — open in editor for manual resolution
# After resolving all conflicts, stage the file and continue
```

### Cherry-Pick Workflow
```bash
# In Commits panel on source branch:
c            # Copy commit (marks it for cherry-pick)
C            # Copy commit range (mark start, then C on end)

# Switch to target branch (Branches panel → space)
v            # Paste (apply all copied commits)
```

### Bisect
```bash
# In Commits panel:
b            # Start bisect (mark current commit as bad)
# Navigate to a known-good commit → mark good
# lazygit checks out the midpoint automatically
# Mark each as good/bad until the culprit is found
```

### Worktrees
```bash
# In the worktrees panel (W key from any panel):
n            # Create a new worktree
space        # Switch to worktree
d            # Remove worktree
```

### Custom Commands
```yaml
# ~/.config/lazygit/config.yml
customCommands:
  - key: "C"
    command: "git commit -m '{{index .PromptResponses 0}}'"
    context: "files"
    prompts:
      - type: "input"
        title: "Commit message"
  - key: "<c-r>"
    command: "gh pr create --fill"
    context: "files"
    description: "Open PR on GitHub"
```

### Reviewing AI-Generated Diffs
```bash
# After applying an AI-suggested patch or large diff:
# 1. Open lazygit — the Files panel shows changed files
# 2. Press Enter on each file to expand the diff
# 3. Use line-level staging (v mode) to accept only the parts you want
# 4. Stage approved hunks, discard unwanted ones with d
# 5. Commit staged portion, leaving the rest for review
```

### Bulk Operations
```bash
# Stage all files:         a  (in Files panel)
# Discard all changes:     d  (in Files panel, on "all files" row)
# Drop multiple commits:   select with space → d (in Commits panel)
# Delete multiple branches: select with space → d (in Branches panel)
```

## Practical Examples

```bash
# Launch lazygit in current repo
lazygit

# Launch in a specific directory
lazygit -p /path/to/repo

# Launch with a specific git config
LG_CONFIG_FILE=~/.config/lazygit/work.yml lazygit
```

### Typical Commit Workflow
```
1. Files panel shows unstaged changes
2. Press Enter on a file to review diff
3. Use v + space to stage specific lines
4. Press Esc to return to Files panel
5. Press c to commit → type message → Enter
6. Press P to push
```

## Configuration

```yaml
# ~/.config/lazygit/config.yml
gui:
  theme:
    activeBorderColor: ["green", "bold"]
  showFileTree: true
  splitDiff: "auto"
git:
  paging:
    colorArg: always
    pager: delta --dark --paging=never   # use delta as pager
  commit:
    signOff: false
  merging:
    manualCommit: false
  log:
    order: "topo-order"
```

## Chaining with Other Skills

- **gh (GitHub CLI):** Bind a custom command to run `gh pr create` or `gh pr view` from within lazygit's files panel
- **ripgrep (cli-ripgrep):** Use rg to find which files contain a pattern before opening lazygit to selectively stage only relevant hunks
- **fd (cli-fd):** Use fd to locate files that changed before opening lazygit focused on that path with `lazygit -p`
- **delta:** Set `git.paging.pager: delta` in lazygit config for side-by-side diffs with syntax highlighting inside the TUI
