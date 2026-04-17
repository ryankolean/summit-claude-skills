---
name: cli-bat
description: >
  Covers effective use of bat, the syntax-highlighting cat
  replacement, for viewing files, previewing diffs, using as a MANPAGER,
  integrating with fzf previews, and customizing themes. Activates when the
  user asks about bat, syntax-highlighted file viewing, or replacing cat/less.
---

# bat — cat with Syntax Highlighting

**Repo:** https://github.com/sharkdp/bat

A `cat` clone with syntax highlighting, Git integration, line numbers, and
automatic paging. Drop-in replacement for `cat` with a much better reading
experience for source code, configs, and diffs.

## When to Activate

**Manual triggers:**
- "How do I use bat?"
- "Syntax highlight a file in the terminal"
- "Better cat / better less"
- "View a file with line numbers"

**Auto-detect triggers:**
- User wants to view source files with highlighting in the terminal
- User is building fzf previews that need syntax highlighting
- User wants to use bat as a pager for man pages or git diff
- User wants to inspect non-printable characters in a file
- User wants to view only a range of lines from a large file

## Key Commands

### Basic Usage
```bash
bat file.py                      # View file with syntax highlighting + line numbers
bat file1.py file2.py            # View multiple files
bat -l json file.txt             # Force language (json, python, yaml, etc.)
bat -n file.py                   # Show line numbers only (no decorations)
bat -A file.py                   # Show non-printable chars (tabs, spaces, newlines)
bat -p file.py                   # Plain output (no line numbers, no header, no pager)
bat --diff file.py               # Show only lines changed vs Git (requires git repo)
bat -r 10:50 file.py             # Show only lines 10–50
bat -r 10: file.py               # Show from line 10 to end
bat -r :50 file.py               # Show first 50 lines
bat --list-languages             # List all supported languages
bat --list-themes                # List all available themes
```

### Output Control
```bash
bat -P file.py                   # Disable pager (print directly, like cat)
bat --paging=never file.py       # Same as -P
bat --paging=always file.py      # Always use pager even for short files
bat --wrap=never file.py         # No line wrapping (scroll horizontally)
bat --tabs 4 file.py             # Set tab width to 4 spaces
bat --style=plain file.py        # No line numbers, no Git marks, no header
bat --style=numbers,header file.py  # Only specific decorations
```

### Theming
```bash
bat --theme=TwoDark file.py      # Use a specific theme
bat --theme=ansi file.py         # ANSI colors (good for light/dark compatibility)
bat --theme=GitHub file.py       # GitHub-style theme
BAT_THEME="TwoDark" bat file.py  # Set via env var (put in .bashrc/.zshrc)
bat --list-themes | fzf          # Interactively preview themes
```

## Advanced Patterns

### Use bat as MANPAGER
```bash
# In ~/.bashrc or ~/.zshrc:
export MANPAGER="sh -c 'col -bx | bat -l man -p'"
export MANROFFOPT="-c"

# Now man pages render with bat's syntax highlighting:
man ls
man grep
```

### Use bat as Git Diff Pager
```bash
# Preview staged/unstaged changes with syntax highlighting:
git diff | bat --language=diff
git diff HEAD | bat -l diff --style=plain

# Set bat as the default git pager:
git config --global core.pager "bat --style=plain"
# Or just for diff:
git config --global pager.diff "bat"
git config --global pager.log "bat"
```

### fzf Preview Integration
```bash
# Use bat for syntax-highlighted file previews in fzf:
fzf --preview 'bat --color=always {}'

# With line-range preview centered on a match (for rg output):
rg --line-number '' | fzf \
  --delimiter ':' \
  --preview 'bat --color=always --highlight-line {2} {1}' \
  --preview-window 'up,60%,border-bottom,+{2}+3/3'

# Open the selected file at the matching line in $EDITOR:
rg --line-number '' | fzf \
  --delimiter ':' \
  --preview 'bat --color=always --highlight-line {2} {1}' | \
  awk -F: '{print "+"$2" "$1}' | xargs $EDITOR
```

### Piping from curl / Remote Files
```bash
# View an API response with JSON highlighting:
curl -s https://api.example.com/data | bat -l json

# Highlight a shell script fetched from remote:
curl -s https://raw.githubusercontent.com/.../script.sh | bat -l sh

# View a local response body saved to file:
http GET api.example.com/endpoint | bat -l json
```

### Custom Themes
```bash
# Theme files go in bat's config dir:
bat --config-dir        # Shows path (e.g., ~/.config/bat)
mkdir -p $(bat --config-dir)/themes

# Drop .tmTheme or .sublime-color-scheme files there, then:
bat cache --build       # Rebuild theme cache

# Use your custom theme:
bat --theme=MyTheme file.py
```

### bat Config File
```bash
# ~/.config/bat/config
--theme=TwoDark
--style=numbers,changes,header
--paging=auto
--map-syntax "*.conf:INI"
--map-syntax "*.env:Dotenv"
--map-syntax "Dockerfile*:Dockerfile"
```

### Show Non-Printable Characters
```bash
bat -A file.txt      # Tabs shown as ^I, line endings as $, spaces as ·
bat -A *.sh          # Good for spotting Windows line endings (CRLF)
```

## Practical Examples

### Daily Workflows
```bash
# Quick syntax-highlighted view of any config:
bat ~/.ssh/config
bat /etc/hosts
bat package.json

# Preview last 20 lines of a log:
bat -r -20: app.log

# Compare two files side-by-side (combine with diff):
diff <(bat -p file1.py) <(bat -p file2.py)

# View a range and pipe to clipboard:
bat -r 10:30 -p main.py | pbcopy
```

### Aliases (add to .bashrc/.zshrc)
```bash
alias cat='bat --paging=never'     # Replace cat with bat
alias catp='bat -p --paging=never' # bat with no decorations (truly cat-like)
alias batn='bat -n'                # Line numbers only
alias bata='bat -A'                # Show non-printable chars
```

## Chaining with Other Skills

- **fzf (cli-fzf):** Use `--preview 'bat --color=always {}'` to get syntax-highlighted previews inside any fzf selection UI
- **fd (cli-fd):** `fd -e py | xargs bat` to view all Python files with highlighting; `fd -e md | fzf --preview 'bat --color=always {}'` for interactive selection
- **ripgrep (cli-ripgrep):** Combine rg's line-number output with bat's `--highlight-line` for pinpoint preview of search matches
- **git:** Set `core.pager=bat` or `pager.diff=bat` for syntax-highlighted git output across all git commands
