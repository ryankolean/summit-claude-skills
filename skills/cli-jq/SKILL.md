---
name: cli-jq
description: >
  Teach Claude how to effectively use jq for processing, filtering, and
  transforming JSON data. Activates when the user asks about jq, parsing JSON
  in the terminal, reshaping API responses, or transforming structured data
  with filters, pipes, select, map, or reduce.
---

# jq — JSON Processor

**Repo:** https://github.com/jqlang/jq

Lightweight, powerful command-line JSON processor. Like `sed` for JSON: slice,
filter, map, and transform structured data with a compact expression language.
Reads JSON (or NDJSON), applies a filter, and outputs JSON (or plain text).

## When to Activate

**Manual triggers:**
- "How do I use jq?"
- "Parse this JSON response"
- "Extract fields from JSON"
- "Filter/reshape an API response"

**Auto-detect triggers:**
- User is processing curl, gh, or httpie output and wants specific fields
- User has a JSON file and wants to extract or transform data
- User is scripting against an API and needs to reshape the response
- User wants to convert JSON to CSV or TSV

## Key Commands

### Running jq
```bash
jq '.' file.json                     # Pretty-print JSON
jq '.' <<< '{"a":1}'                # From string (herestring)
curl -s url | jq '.'                 # Pipe from curl
jq -r '.name' file.json              # Raw output (no quotes around strings)
jq -c '.'                            # Compact output (single line)
jq -n '{a: 1}'                       # No input — construct JSON from scratch
jq --arg name "Alice" '{name: $name}' # Pass shell variable as string
jq --argjson count 42 '{count: $count}' # Pass shell variable as JSON
jq -s '.'                            # Slurp: read all inputs into an array
jq -e '.exists' && echo "found"     # Exit code 1 if output is false/null
```

### Basic Filters
```bash
jq '.key'                            # Field access
jq '.a.b.c'                          # Nested field
jq '.items[0]'                       # Array index
jq '.items[-1]'                      # Last element
jq '.items[2:5]'                     # Slice (indices 2,3,4)
jq '.items[]'                        # Iterate array elements (one per line)
jq '.[] | .name'                     # Iterate and extract field
jq 'keys'                            # Array of object keys
jq 'values'                          # Array of object values
jq 'length'                          # Array length or string length
jq 'has("key")'                      # Test key existence
jq 'in({"a":1})'                     # Test if value is a key
jq 'type'                            # "array", "object", "string", "number", "boolean", "null"
```

### Pipes and Construction
```bash
jq '.users[] | .email'               # Pipe: iterate then extract
jq '.users[] | {name, email}'        # Construct object with same-name fields
jq '.users[] | {n: .name, e: .email}' # Construct with renamed fields
jq '[.users[] | .name]'              # Collect into array
jq '{count: (.users | length)}'      # Object with computed value
```

### String Operations
```bash
jq '.name | ascii_downcase'
jq '.name | ascii_upcase'
jq '.name | ltrimstr("prefix")'
jq '.name | rtrimstr("suffix")'
jq '.name | split(" ")'              # Split string → array
jq '.parts | join(", ")'             # Array → string
jq '.name | test("^foo")'            # Regex test (returns boolean)
jq '.name | match("(\\w+)@(\\w+)")'  # Regex match with captures
jq '.name | gsub("foo"; "bar")'      # Global substitution
jq '"Hello \(.name)!"'               # String interpolation
jq '@uri'                            # URL-encode a string
jq '@html'                           # HTML-escape a string
jq '@base64'                         # Base64-encode
jq '@base64d'                        # Base64-decode
```

### select and Conditionals
```bash
jq '.[] | select(.age > 30)'         # Filter: keep items where age > 30
jq '.[] | select(.status == "active")'
jq '.[] | select(.name | startswith("A"))'
jq '.[] | select(.tags | contains(["go"]))'
jq '.[] | select(.score != null)'    # Exclude null
jq 'if .age > 18 then "adult" else "minor" end'
jq '.value // "default"'             # Alternative: use "default" if null/false
jq 'if . == null then empty else . end' # Drop nulls (empty suppresses output)
```

### map and Arrays
```bash
jq 'map(.name)'                      # Transform every element
jq 'map(select(.active))'            # Filter array
jq 'map(. * 2)'                      # Double every number
jq 'map({name: .name, upper: (.name | ascii_upcase)})'
jq '[.[] | .score] | add'            # Sum all scores
jq '[.[] | .score] | add / length'   # Average
jq 'min_by(.score)'                  # Object with minimum score
jq 'max_by(.score)'
jq 'sort_by(.name)'                  # Sort array by field
jq 'sort_by(.created_at) | reverse' # Newest first
jq 'unique_by(.email)'               # Deduplicate by field
jq 'group_by(.department)'           # Group into nested arrays
jq 'flatten'                         # Flatten nested arrays
jq 'flatten(1)'                      # Flatten one level deep
jq 'first'                           # First element
jq 'last'                            # Last element
jq 'nth(2)'                          # Third element (0-indexed)
jq 'indices(",")'                    # Positions of value in array/string
jq 'any(.[]; . > 10)'                # True if any element > 10
jq 'all(.[]; . > 0)'                 # True if all elements > 0
```

### reduce and Aggregation
```bash
# Sum an array of numbers
jq 'reduce .[] as $x (0; . + $x)'

# Build a lookup map from an array
jq 'reduce .[] as $item ({}; . + {($item.id | tostring): $item})'

# Accumulate matching items
jq 'reduce .[] as $x ([]; if $x.active then . + [$x] else . end)'

# Count occurrences of each status
jq 'reduce .[] as $x ({}; .[$x.status] += 1)'

# group_by + map for frequency table (simpler alternative)
jq 'group_by(.status) | map({status: .[0].status, count: length})'
```

### Object Manipulation
```bash
jq '. + {"extra": "field"}'          # Add/overwrite field
jq 'del(.secret)'                    # Remove field
jq 'del(.a, .b)'                     # Remove multiple fields
jq 'with_entries(select(.value != null))'  # Remove null-valued keys
jq 'with_entries(.value |= . * 2)'   # Transform all values
jq 'with_entries(.key |= "prefix_" + .)' # Rename all keys
jq 'to_entries'                      # [{key,value}, ...]
jq 'from_entries'                    # {key: value, ...}
jq 'to_entries | map(select(.value != "")) | from_entries' # Remove empty strings
```

### Output Formats
```bash
# CSV output
jq -r '.[] | [.name, .age, .city] | @csv'

# TSV output
jq -r '.[] | [.name, .age] | @tsv'

# Formatted table with column alignment (combine with column command)
jq -r '.[] | [.name, .score] | @tsv' | column -t

# NDJSON (newline-delimited JSON) — one JSON object per line
jq -c '.[]' large_array.json         # Explode array to NDJSON
jq -s '.' ndjson_file.json           # Slurp NDJSON back to array
```

## Advanced Patterns

### Reshaping API Responses
```bash
# GitHub: extract PR info
gh pr list --json number,title,author,labels \
  | jq '.[] | {
      pr: .number,
      title,
      author: .author.login,
      labels: [.labels[].name]
    }'

# Flatten nested pagination response
curl -s 'https://api.example.com/data' \
  | jq '.data.items[] | {id, name: .metadata.name}'

# Merge two arrays by a key
jq -n \
  --slurpfile users users.json \
  --slurpfile scores scores.json \
  '($users[0] | map({(.id|tostring): .}) | add) as $u |
   $scores[0] | map(. + $u[(.userId|tostring)])'
```

### Recursive Descent
```bash
jq '.. | .name? // empty'            # Find all "name" fields anywhere in document
jq '.. | numbers'                    # Extract all numbers recursively
jq 'path(.. | .error?)'             # Get path to any "error" field
jq '[leaf_paths]'                    # All paths to leaf nodes
jq 'getpath(["a","b","c"])'          # Get by path array
jq 'setpath(["a","b"]; 42)'          # Set by path array
jq 'delpaths([["a","secret"]])'      # Delete by path array
```

### Custom Functions
```bash
# Define and use a function inline
jq 'def log2: . as $n | 1 | until(. * 2 > $n; . * 2) | log / log(2) | floor;
    .data[] | {value: ., log2: log2}'

# Reusable normalize function
jq 'def normalize($min; $max): (. - $min) / ($max - $min);
    .scores[] | normalize(0; 100)'

# Recursive function
jq 'def depth: if type == "object" or type == "array"
    then [.[]] | map(depth) | max + 1
    else 0 end;
    depth'
```

### try-catch
```bash
jq '.[] | try .value catch "parse error"'
jq 'try (.x / .y) catch "division error"'
jq '.items[] | try {name: .name, score: (.data | fromjson | .score)} catch {name: .name, score: null}'
```

### NDJSON / Streaming Large Files
```bash
# Process a massive JSON array without loading it all into memory
jq -c --stream 'if length == 2 and .[0][-1] == "name" then .[1] else empty end' huge.json

# Combine multiple NDJSON lines
cat *.ndjson | jq -s 'map(select(.type == "event"))'

# Stream and filter
jq -cn --stream 'fromstream(1|truncate_stream(inputs; 1))' huge_array.json
```

## Practical Examples

### Extract and Summarize API Data
```bash
# Count GitHub issues by label
gh issue list --json labels --limit 500 \
  | jq '[.[].labels[].name] | group_by(.) | map({label: .[0], count: length}) | sort_by(-.count)'

# Top 5 repos by stars
gh repo list myorg --json name,stargazerCount --limit 100 \
  | jq 'sort_by(-.stargazerCount) | .[0:5] | .[] | "\(.stargazerCount)\t\(.name)"' -r
```

### Transform Config Files
```bash
# Add a field to every element
jq 'map(. + {env: "production"})' config.json

# Merge two JSON configs (right wins)
jq -s '.[0] * .[1]' base.json overrides.json

# Extract just the keys as a bash array
mapfile -t keys < <(jq -r 'keys[]' config.json)
```

### Validate Data
```bash
# Find records missing required fields
jq '.[] | select((.name == null) or (.email == null)) | {id, missing: [if .name == null then "name" else empty end, if .email == null then "email" else empty end]}' records.json
```

## Chaining with Other Skills

- **gh (cli-gh):** `gh ... --json | jq` is the standard gh power combo — every gh resource supports `--json` output
- **httpie (cli-httpie):** HTTPie outputs JSON that pipes cleanly into jq; use `http GET url | jq '.field'`
- **yq (cli-yq):** Convert YAML → JSON with `yq -o=json`, then process with jq; or go the other way
- **duckdb:** Load NDJSON into DuckDB with `read_json_auto`, or export query results as JSON and reshape with jq
- **fzf (cli-fzf):** Use jq to extract a field (e.g., PR numbers), then pipe into fzf for interactive selection
