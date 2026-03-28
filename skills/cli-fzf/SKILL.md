---
name: cli-fzf
description: >
  Teach Claude how to effectively use fzf (fuzzy finder) for interactive
  filtering of files, command history, processes, git branches, and any
  line-oriented data. Activates when the user asks about fzf, interactive
  selection from lists, fuzzy searching, or filtering command output interactively.
---

# fzf — Fuzzy Finder

**Repo:** https://github.com/junegunn/fzf

Interactive fuzzy finder for the terminal. Pipe anything into fzf and get an
interactive, filterable selection UI. Works with files, history, processes,
git refs, environment variables, and any line-oriented data.

## When to Activate

**Manual triggers:**
- "How do I use fzf?"
- "Fuzzy find files"
- "Interactive selection from a list"
- "Filter command output interactively"

**Auto-detect triggers:**
- User wants to interactively select from a large list of items
- User wants to search command history interactively
- User is combining fd/ripgrep output with selection
- User wants to kill a process by fuzzy-searching ps output
- User wants to switch git branches interactively

## Key Commands

### Basic Usage
```bash
fzf                          # Fuzzy find files in current directory
fzf --height 40%             # Use only 40% of terminal height
fzf --reverse                # Put input at top (prompt at top)
fzf --border                 # Draw border around finder
fzf --query "foo"            # Pre-fill the search query
fzf --filter "foo"           # Non-interactive: filter and print matches
fzf -m                       # Multi-select (Tab to select, Enter to confirm)
fzf --select-1               # Auto-select if only one match
fzf --exit-0                 # Exit immediately if no matches
```

### Shell Integration (set up in .bashrc/.zshrc)
```bash
# CTRL-R — fuzzy history search (replaces default reverse-i-search)
# CTRL-T — fuzzy file paste (paste selected file path into command line)
# ALT-C  — fuzzy cd (cd into selected directory)
$(brew install fzf && $(brew --prefix)/opt/fzf/install)  # installs key bindings
```

### Preview Window
```bash
fzf --preview 'cat {}'                    # Preview file contents
fzf --preview 'bat --color=always {}'    # Preview with syntax highlighting
fzf --preview 'head -50 {}'             # Preview first 50 lines
fzf --preview-window=right:60%          # Preview on right, 60% width
fzf --preview-window=up:30%             # Preview at top, 30% height
fzf --preview 'ls -la {}'               # Preview directory contents
```

### Key Bindings
```bash
fzf --bind 'ctrl-a:select-all'          # CTRL-A selects all
fzf --bind 'ctrl-d:deselect-all'        # CTRL-D deselects all
fzf --bind 'ctrl-/:toggle-preview'      # Toggle preview window
fzf --bind 'ctrl-y:execute(echo {} | pbcopy)'  # Copy selection to clipboard
fzf --bind 'ctrl-o:execute(open {})'    # Open selected file
```

## Advanced Patterns

### Integration with fd (faster find)
```bash
# Use fd as fzf's default file finder (faster, respects .gitignore)
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

# Interactive file selection using fd
fd --type f | fzf --preview 'bat --color=always {}'
```

### Integration with ripgrep (search then select)
```bash
# Search file contents, then select a match
rg --line-number '' | fzf --delimiter ':' --preview 'bat --color=always --highlight-line {2} {1}'

# Live ripgrep as you type (reload on query change)
fzf --disabled --ansi \
    --bind "change:reload:rg --color=always --line-number {q} || true" \
    --delimiter ':' \
    --preview 'bat --color=always --highlight-line {2} {1}'
```

### Kill a Process
```bash
# Fuzzy-select a process and kill it
kill -9 $(ps aux | fzf | awk '{print $2}')

# More user-friendly version
ps aux | fzf --header-lines=1 | awk '{print $2}' | xargs kill -9
```

### Git Branch Switching
```bash
# Interactively checkout a git branch
git branch | fzf | xargs git checkout

# Include remote branches
git branch -a | sed 's/remotes\/origin\///' | fzf | xargs git checkout

# With diff preview
git branch | fzf --preview 'git log --oneline --graph --date=short --color=always {}'
```

### Git Log Navigation
```bash
# Browse git log and show diff on preview
git log --oneline --color=always | \
  fzf --ansi --preview 'git show --color=always {1}' | \
  awk '{print $1}' | xargs git show
```

### Environment Variable Selection
```bash
# Select and print an environment variable
env | fzf | cut -d= -f1
printenv $(env | fzf | cut -d= -f1)
```

### SSH Host Selection
```bash
# Fuzzy-select an SSH host from known_hosts
ssh $(awk '{print $1}' ~/.ssh/known_hosts | tr ',' '\n' | fzf)
```

### Docker Container/Image Selection
```bash
# Select and exec into a running container
docker exec -it $(docker ps | fzf --header-lines=1 | awk '{print $1}') bash

# Remove docker images interactively
docker images | fzf -m --header-lines=1 | awk '{print $3}' | xargs docker rmi
```

### tmux Integration
```bash
# Switch tmux sessions interactively
tmux list-sessions | fzf | cut -d: -f1 | xargs tmux switch-client -t

# Switch tmux windows
tmux list-windows | fzf | cut -d: -f1 | xargs tmux select-window -t
```

## Practical Examples

### Daily Workflows
```bash
# Open a file in your editor (fuzzy search project files)
$EDITOR $(fzf --preview 'bat --color=always {}')

# cd into any directory under current path
cd $(find . -type d | fzf)

# Copy file path to clipboard
fzf | pbcopy

# Source a shell script after selecting it
source $(find . -name '*.sh' | fzf)
```

### FZF with Custom Input
```bash
# Select from a custom list
echo -e "option1\noption2\noption3" | fzf

# Select from array
items=("apple" "banana" "cherry")
printf '%s\n' "${items[@]}" | fzf

# Confirm before running: select npm script to run
cat package.json | jq -r '.scripts | keys[]' | fzf | xargs npm run
```

### Useful Shell Functions
```bash
# Add to .bashrc/.zshrc

# fcd: fuzzy cd
fcd() { cd "$(find ${1:-.} -type d | fzf)" }

# fkill: fuzzy kill
fkill() { kill -9 $(ps aux | fzf | awk '{print $2}') }

# flog: fuzzy git log with checkout
flog() {
  git log --oneline --color=always | fzf --ansi | awk '{print $1}' | xargs git checkout
}

# fenv: fuzzy env var lookup
fenv() { printenv $(env | fzf | cut -d= -f1) }
```

## Configuration (~/.fzf.bash or ~/.fzf.zsh)

```bash
# Default options
export FZF_DEFAULT_OPTS='
  --height 40%
  --layout=reverse
  --border
  --preview-window=right:50%:wrap
  --bind ctrl-/:toggle-preview
'

# Use fd for file finding
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
```

## Chaining with Other Skills

- **fd (cli-fd):** Use fd to generate a file list respecting .gitignore, pipe into fzf for interactive selection — far faster than `find | fzf`
- **ripgrep (cli-ripgrep):** Use rg to search file contents, pipe results into fzf for interactive navigation to the exact line
- **bat:** Use `--preview 'bat --color=always {}'` for syntax-highlighted file previews in fzf
- **git/gh:** Pipe `git branch`, `git log`, `gh pr list` into fzf for interactive git workflows
