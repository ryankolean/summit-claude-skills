---
name: cli-fd
description: >
  Teach Claude how to effectively use fd as a modern, fast replacement for
  `find`. Covers fd PATTERN, -e ext, -t type, -H hidden, -I no-ignore, -x exec,
  -X batch exec, -E exclude, --changed-within, -d depth, --size, bulk operations,
  exec placeholders, and combining with ripgrep, bat, and fzf. Activates when the
  user asks about fd, finding files by name/type/date/size, or running commands
  on matched files.
---

# fd — Modern `find` Replacement

**Repo:** https://github.com/sharkdp/fd

`fd` is a simple, fast alternative to `find`. It uses Rust regex for pattern
matching, respects `.gitignore` by default, colorizes output, and has an
intuitive interface. Replaces the majority of `find` use cases with far less
typing.

## When to Activate

**Manual triggers:**
- "How do I use fd?"
- "Find files by name / extension / type"
- "Find files changed recently"
- "Run a command on all files matching a pattern"

**Auto-detect triggers:**
- User wants to locate files in a project tree
- User wants to filter by file extension, size, or modification time
- User wants to run a command on every matched file
- User is building a pipeline with ripgrep, bat, or fzf

## Key Commands

### Basic Search
```bash
fd                                  # list all non-hidden files recursively
fd 'config'                         # files whose name contains "config" (regex)
fd '^config\.'                      # name starts with "config."
fd 'test' src/                      # search only in src/
fd 'README' ~ /tmp                  # search multiple directories
```

### Filter by Extension and Type
```bash
fd -e ts                            # only TypeScript files (-e, --extension)
fd -e ts -e tsx                     # multiple extensions
fd -t f                             # files only (-t f)
fd -t d                             # directories only (-t d)
fd -t l                             # symlinks only (-t l)
fd -t x                             # executable files (-t x)
fd -t e                             # empty files/directories (-t e)
fd -e json -t f 'schema'            # .json files with "schema" in name
```

### Hidden & Ignored Files
```bash
fd -H 'dotfile'                     # include hidden files (dotfiles)
fd -I 'node_modules'                # disable .gitignore (--no-ignore)
fd -HI '.env'                       # include hidden AND ignored files
fd --no-ignore-vcs 'build'          # ignore .gitignore but honor .fdignore
```

### Depth & Size
```bash
fd -d 2 'config'                    # max depth 2 from current dir
fd --min-depth 2 'test'             # skip top-level results
fd --size +1mb -t f                 # files larger than 1 MB
fd --size -10kb -e log              # log files smaller than 10 KB
fd --size +100kb --size -1mb -t f   # files between 100 KB and 1 MB
```

### Time-Based Filtering
```bash
fd --changed-within 1d              # files modified in last 24 hours
fd --changed-within '1 week'        # modified in last week
fd --changed-before '2024-01-01'    # modified before a date
fd -e log --changed-within 1h       # log files touched in last hour
```

### Excluding Paths
```bash
fd -E node_modules                  # exclude a directory
fd -E '*.test.ts'                   # exclude by pattern
fd -E '.git' -E dist -E node_modules  # multiple exclusions
# Persist exclusions in .fdignore or .gitignore
```

## Executing Commands on Results

### `-x` — Run command per file (parallel by default)
```bash
fd -e png -x convert {} {.}.jpg          # convert each PNG to JPG
fd -e py -x black {}                     # format each Python file
fd 'Makefile' -x make -C {//}           # run make in each dir containing Makefile
fd -e ts -x wc -l                        # count lines in each TS file
```

### Exec Placeholders
| Placeholder | Meaning |
|-------------|---------|
| `{}`        | full path (`./src/app.ts`) |
| `{/}`       | filename only (`app.ts`) |
| `{//}`      | parent directory (`./src`) |
| `{.}`       | path without extension (`./src/app`) |
| `{/.}`      | filename without extension (`app`) |

### `-X` — Batch exec (all results as one invocation)
```bash
fd -e ts -X eslint                   # pass all .ts files to eslint at once
fd -e md -X prettier --write         # format all markdown files
fd -t f -e log -X rm                 # delete all log files (careful!)
fd -e ts -X wc -l | sort -rn | head  # total lines; sort largest first
```

### Pipe to xargs
```bash
fd -e json | xargs jq '.version'             # print version from each package.json
fd -e ts -0 | xargs -0 grep -l 'useEffect'  # safe with spaces via NUL separator
fd -e ts | xargs -P4 tsc --noEmit            # parallel type-check with 4 workers
```

## Advanced Patterns

### Bulk Rename
```bash
# Rename all .jpeg to .jpg
fd -e jpeg -x mv {} {.}.jpg

# Add a prefix to all test files
fd 'spec\.ts$' -x mv {} {//}/new_{/}

# Use prename/rename for complex patterns
fd -e ts | xargs rename 's/Component/Widget/g'
```

### Bulk Archive / Copy
```bash
# Copy all .env.example files, stripping .example
fd '.env.example' -x cp {} {.}

# Archive all markdown docs
fd -e md -X tar czf docs.tar.gz
```

### Find Large Directories (disk usage)
```bash
fd -t d -d 1 | xargs du -sh | sort -rh | head -20
```

### Count Files by Extension
```bash
fd -t f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
```

### Find Duplicate Filenames
```bash
fd -t f -x basename {} | sort | uniq -d
```

### Search, Then Open in Editor
```bash
# Find a TypeScript file and open in VS Code
code $(fd -e ts 'UserService')

# Multi-select with fzf
fd -e ts | fzf -m | xargs code
```

### Integration with ripgrep
```bash
# Find .ts files then search inside them (useful for large monorepos)
fd -e ts --changed-within 1d | xargs rg 'TODO'

# Files without tests (no .test. counterpart) — rough check
fd -e ts -E '*.test.ts' -E '*.spec.ts' src/ | while read f; do
  [[ ! -f "${f%.ts}.test.ts" ]] && echo "missing test: $f"
done
```

## Practical Examples

### Pre-commit Cleanup
```bash
# Delete all compiled output before commit
fd -e js -E 'node_modules' dist/ -X rm
fd __pycache__ -t d -X rm -rf
```

### Watch for New Files (poll approach)
```bash
while true; do
  fd --changed-within 5s -e ts | xargs -r npx tsc --noEmit
  sleep 5
done
```

### List Files Ignored by Git (find what .gitignore hides)
```bash
fd -I --type f | rg --files-without-match '.' --no-ignore
# Simpler: git status --short | grep '^ ' | awk '{print $2}'
```

### Quick Project Stats
```bash
echo "=== File counts by type ==="
for ext in ts js py go rs; do
  count=$(fd -e $ext -t f | wc -l)
  echo "  .$ext: $count"
done
```

## Configuration (`.fdignore`)

```
# .fdignore — same syntax as .gitignore, placed at project root or ~/.config/fd/ignore
node_modules/
dist/
.next/
.cache/
*.min.js
*.d.ts
coverage/
```

## Chaining with Other Skills

- **ripgrep (cli-ripgrep):** Use `fd` to select files (by type, date, size), then pipe to `rg` for content search — cleaner and faster than `rg -g` globs for complex file filters.
- **bat:** `fd -e md | xargs bat --language=md` — syntax-highlighted preview of all markdown files.
- **fzf (cli-fzf):** Set `FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'` so fzf uses fd for file listing; also pipe `fd` results into fzf for interactive selection.
