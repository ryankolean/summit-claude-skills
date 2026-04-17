---
name: cli-ripgrep
description: >
  Covers effective use of ripgrep (rg) for fast regex search across
  codebases. Covers rg PATTERN, -i, -w, -l, -c, -n, --type, -g, -A/-B/-C,
  -U multiline, --json, type-add, .ripgreprc, replacement, and PCRE2. Activates
  when the user asks about ripgrep, rg, fast code search, or searching file
  contents with regex while respecting .gitignore.
---

# ripgrep (rg) — Fast Regex Search

**Repo:** https://github.com/BurntSushi/ripgrep

ripgrep recursively searches directories for a regex pattern. It is faster than
grep/ack/ag, respects `.gitignore` by default, and outputs colorized results.
Drop-in replacement for `grep -r` in virtually all code-search workflows.

## When to Activate

**Manual triggers:**
- "How do I use ripgrep / rg?"
- "Search for a pattern across my codebase"
- "Find all files containing X"

**Auto-detect triggers:**
- User wants to search file contents recursively in a project
- User wants to filter results by file type or extension
- User needs multiline or PCRE2 regex search
- User wants to pipe search results to jq or fzf

## Key Commands

### Basic Search
```bash
rg 'TODO'                           # search current dir recursively
rg 'TODO' src/                      # search in src/ only
rg 'TODO' src/app.ts                # search a single file
rg 'func\w+' --type=go              # search only Go files
rg -i 'error'                       # case-insensitive
rg -w 'log'                         # whole word only (not "logger")
rg -F 'foo.bar'                     # fixed string, no regex (literal dots etc.)
```

### Controlling Output
```bash
rg -l 'TODO'                        # list matching file paths only
rg -L 'TODO'                        # list files WITHOUT a match
rg -c 'TODO'                        # count matches per file
rg -n 'TODO'                        # show line numbers (default: on)
rg --no-filename 'TODO'             # suppress filename prefix
rg --no-heading 'TODO'              # one match per line (grep-style)
rg -o 'v\d+\.\d+\.\d+'             # print only the matched portion
rg --max-count=1 'TODO'             # stop after first match per file
```

### Context Lines
```bash
rg -A 3 'def main'                  # 3 lines After each match
rg -B 3 'def main'                  # 3 lines Before each match
rg -C 5 'panic'                     # 5 lines of Context (before + after)
```

### File Type Filtering
```bash
rg 'import' --type=js               # built-in type: js, py, rust, go, ts, etc.
rg 'import' -t js -t ts             # multiple types
rg 'import' --type-not=json         # exclude a type
rg 'TODO' -g '*.md'                 # glob pattern: only .md files
rg 'TODO' -g '!*.test.*'            # glob pattern: exclude test files
rg 'secret' -g '**/.env*'          # search hidden env files specifically
```

### Custom Type Definitions
```bash
rg --type-add 'web:*.{html,css,js,ts}' -t web 'className'  # one-off custom type

# Persist in ~/.ripgreprc:
# --type-add=web:*.{html,css,js,ts,jsx,tsx}
```

### Multiline Search (`-U`)
```bash
rg -U 'function\s+\w+\s*\([^)]*\)\s*\{' --type=js   # match multi-line function signature
rg -U 'SELECT.*\n.*FROM'            # SQL spanning two lines
# Note: -U disables line-by-line mode; combine with --multiline-dotall for . to match \n
```

### JSON Output
```bash
rg --json 'TODO'                    # emit newline-delimited JSON objects
rg --json 'TODO' | jq 'select(.type=="match") | .data.lines.text'
rg --json -l 'FIXME' | jq -r 'select(.type=="begin") | .data.path.text'
```

### Replacement (non-destructive preview)
```bash
rg 'foo' --replace 'bar'            # print lines with replacement applied (no file change)
rg 'v(\d+)' --replace 'version-$1' # backreferences with $1, $2, ...
# To actually replace in files, pipe to sed or use sd:
rg -l 'oldName' | xargs sed -i '' 's/oldName/newName/g'
```

### PCRE2 (advanced regex)
```bash
rg -P '(?<=def )\w+'               # lookbehind
rg -P '\bfoo\b(?!bar)'             # negative lookahead
rg -P '(\w+)\s+\1'                 # backreference (repeated word)
# Install with: brew install ripgrep (macOS ships PCRE2-enabled builds)
```

### Hidden Files & Ignored Paths
```bash
rg -H 'secret' --hidden             # include hidden files (.dotfiles)
rg 'TODO' -I                        # ignore binary files (default behavior, explicit)
rg 'TODO' --no-ignore               # disable .gitignore/.ignore processing
rg 'TODO' --no-ignore-vcs           # disable VCS ignores only
rg 'TODO' -u                        # -u = --no-ignore; -uu also searches hidden
rg 'TODO' -uuu                      # equivalent to grep -r (ignore everything)
```

### Searching Compressed / Stdin
```bash
rg 'error' --search-zip file.gz     # search inside gzip files
cat file.log | rg 'ERROR'           # search stdin
```

## Advanced Patterns

### Find All TODOs Across a Project (structured)
```bash
rg --json 'TODO:\s*(.+)' | \
  jq -r 'select(.type=="match") | [.data.path.text, (.data.line_number|tostring), .data.submatches[0].match.text] | @tsv'
```

### List All Imported Packages (Node)
```bash
rg --no-filename -o "from ['\"]([^'\"]+)['\"]" -r '$1' --type=ts | sort -u
```

### Find Large Functions (heuristic: > 50 lines between braces)
```bash
# Find opening lines of functions — count manually or combine with wc
rg -n '^(export\s+)?(async\s+)?function ' --type=ts
```

### Search + Immediate Edit (with fzf)
```bash
rg --line-number '' | \
  fzf --delimiter ':' \
      --preview 'bat --color=always --highlight-line {2} {1}' | \
  awk -F: '{print $1 " +" $2}' | xargs $EDITOR
```

### `.ripgreprc` Config File
```ini
# ~/.ripgreprc — set RIPGREP_CONFIG_PATH=~/.ripgreprc in your shell profile
--type-add=web:*.{html,css,js,ts,jsx,tsx,vue,svelte}
--type-add=config:*.{json,yaml,yml,toml,ini}
--smart-case
--hidden
--glob=!.git/
--glob=!node_modules/
--glob=!dist/
--colors=path:fg:blue
--colors=match:fg:red
--colors=match:style:bold
```

## Practical Examples

### Find All API Endpoints in a Node Project
```bash
rg "(app|router)\.(get|post|put|delete|patch)\s*\(" --type=js --type=ts -n
```

### Find Hardcoded Secrets (naive scan)
```bash
rg -i '(password|secret|api_key|token)\s*[:=]\s*["\x27][^\s"]+["\x27]' \
   --glob='!*.test.*' --glob='!*.spec.*'
```

### Count Lines of Code by Type
```bash
rg '' --type=ts -l | xargs wc -l | sort -rn | head -20
```

### Diff Search: What Changed in Last Commit
```bash
git diff HEAD~1 | rg '^\+.*TODO'   # new TODOs introduced in last commit
```

## Chaining with Other Skills

- **fd (cli-fd):** Use `fd` to select a file set, then pipe to `rg` for content search — e.g., `fd -e ts | xargs rg 'useEffect'`
- **jq:** Pipe `rg --json` output to jq for structured extraction of match text, file, and line numbers
- **fzf (cli-fzf):** Pipe `rg` results into fzf for interactive navigation directly to the matched line in your editor
