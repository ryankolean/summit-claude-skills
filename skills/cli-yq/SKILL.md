---
name: cli-yq
description: >
  Teach Claude how to effectively use yq for reading, writing, and transforming
  YAML, JSON, XML, TOML, and CSV files. Activates when the user asks about yq,
  editing YAML configs, patching Kubernetes manifests, merging compose files,
  or converting between structured data formats.
---

# yq — YAML/JSON/XML/TOML Processor

**Repo:** https://github.com/mikefarah/yq

Portable command-line YAML processor. Uses jq-like syntax to read, update,
merge, and convert YAML (and JSON, XML, TOML, CSV). The go-to tool for
patching Kubernetes manifests, Docker Compose files, and CI/CD configs in
scripts without a full templating engine.

## When to Activate

**Manual triggers:**
- "How do I use yq?"
- "Edit a YAML file from the command line"
- "Patch a Kubernetes manifest"
- "Convert YAML to JSON"

**Auto-detect triggers:**
- User wants to read or update YAML config without opening an editor
- User is scripting Kubernetes manifest generation or patching
- User wants to merge multiple YAML files
- User wants to substitute environment variables into YAML
- User needs to convert between YAML, JSON, TOML, or XML

## Key Commands

### Running yq
```bash
yq '.' file.yaml                     # Pretty-print YAML
yq -o=json '.' file.yaml            # Output as JSON
yq -o=yaml '.' file.json            # Convert JSON to YAML
yq -P '.' file.json                  # Pretty-print (alias for -o=yaml)
yq -i '.' file.yaml                  # In-place edit
yq -e '.key' file.yaml              # Exit 1 if result is null/false
yq --no-colors '.' file.yaml        # Disable colored output (for piping)
yq '.' *.yaml                        # Process multiple files
cat file.yaml | yq '.'              # Read from stdin
```

### Reading Values
```bash
yq '.key' file.yaml
yq '.a.b.c' file.yaml               # Nested access
yq '.items[0]' file.yaml            # Array index
yq '.items[-1]' file.yaml           # Last element
yq '.items[0].name' file.yaml       # Nested in array
yq '.items[] | .name' file.yaml     # Iterate and extract
yq 'keys' file.yaml                  # List all top-level keys
yq '.map | keys' file.yaml
yq 'length' file.yaml                # Length of array/string
yq '.items | length' file.yaml
yq '. | type' file.yaml              # "map", "seq", "str", "int", "bool", "null"
```

### Updating Values (in-place)
```bash
yq -i '.image.tag = "v2.0.0"' deployment.yaml
yq -i '.replicas = 3' deployment.yaml
yq -i '.env[] |= . + " --verbose"' config.yaml   # Append to each env entry
yq -i '.items += ["new-item"]' file.yaml          # Append to array
yq -i 'del(.obsoleteKey)' file.yaml               # Delete a field
yq -i 'del(.items[2])' file.yaml                  # Delete array element
yq -i '.metadata.labels.version = env(VERSION)' manifest.yaml  # From env var
```

### Adding and Deleting
```bash
yq '. + {"newKey": "value"}' file.yaml
yq '.items += [{"name": "extra"}]' file.yaml
yq 'del(.secret)'
yq 'del(.items[] | select(.name == "remove-me"))'
yq '.items[] |= select(.active)'     # Keep only active items (filter in place)
```

### Array Operations
```bash
yq '.items[]' file.yaml              # Iterate
yq '.items | length' file.yaml
yq '.items[0:3]' file.yaml           # Slice
yq '.items | sort' file.yaml         # Sort (strings/numbers)
yq '.items | sort_by(.name)' file.yaml
yq '.items | reverse' file.yaml
yq '.items | unique' file.yaml
yq '.items | unique_by(.id)' file.yaml
yq '[.items[] | select(.enabled)]' file.yaml   # Filter into array
yq '.items | map(. * 2)' file.yaml   # Transform all elements
yq '.items | map(select(. > 5))' file.yaml
```

### String Operations
```bash
yq '.name | upcase' file.yaml
yq '.name | downcase' file.yaml
yq '.name | split(" ")' file.yaml
yq '.parts | join("-")' file.yaml
yq '.name | test("^prefix")' file.yaml         # Regex test
yq '.name | sub("old","new")' file.yaml        # Replace first
yq '.name | gsub("old","new")' file.yaml       # Replace all
yq '"prefix-" + .name' file.yaml              # String concatenation
yq '.items[] | .name + "=" + .value' file.yaml # Interpolation with +
```

### Format Conversion
```bash
# YAML → JSON
yq -o=json '.' file.yaml

# JSON → YAML
yq -o=yaml '.' file.json
# or shorthand
yq '.' file.json            # yq auto-detects JSON input and outputs YAML

# YAML → TOML
yq -o=toml '.' file.yaml

# TOML → YAML
yq '.' file.toml

# YAML → XML
yq -o=xml '.' file.yaml

# XML → YAML
yq '.' file.xml

# YAML → CSV (array of maps)
yq -o=csv '.items[] | [.name, .count]' file.yaml

# YAML → TSV
yq -o=tsv '.items[] | [.name, .value]' file.yaml
```

### Environment Variable Substitution
```bash
# Substitute env vars in YAML output (does NOT modify file)
VERSION=v2.1.0 yq '.image.tag = env(VERSION)' deployment.yaml

# In-place substitution
APP_PORT=8080 yq -i '.service.port = env(APP_PORT) | .service.port |= . + 0' svc.yaml

# Substitute all occurrences of a placeholder
yq '.spec.template.spec.containers[].image |= sub("IMAGE_TAG"; env(TAG))' deploy.yaml

# envsubst-style: expand ${VAR} syntax in string values (pipe through envsubst)
yq '.' template.yaml | envsubst
```

### Multi-Document YAML
```bash
# yq handles multi-doc YAML (--- separated) natively
yq '.' multi.yaml                   # Process all documents
yq 'select(document_index == 0)' multi.yaml   # First document only
yq 'select(.kind == "Deployment")' manifests.yaml  # Filter by field
yq '. | select(.kind == "Service") | .metadata.name' k8s/*.yaml

# Split multi-doc into separate files
yq 'select(document_index == 0)' multi.yaml > first.yaml
yq 'select(document_index == 1)' multi.yaml > second.yaml
```

### Merging Files
```bash
# Merge two YAML files (second file wins on conflict)
yq '. *+ load("overrides.yaml")' base.yaml

# Deep merge
yq '. *d load("patch.yaml")' base.yaml

# Merge array (concatenate, not replace)
yq '. *+ {"items": [{"extra": true}]}' file.yaml

# Combine multiple files into one multi-doc
cat *.yaml | yq '.'

# Merge all YAML files in directory into array
yq -s '.' *.yaml
```

## Advanced Patterns

### Kubernetes Manifests
```bash
# Patch image tag across all containers
yq -i '.spec.template.spec.containers[].image |= sub(":.*$"; ":" + env(TAG))' deploy.yaml

# Set resource limits
yq -i '
  .spec.template.spec.containers[0].resources = {
    "requests": {"cpu": "100m", "memory": "128Mi"},
    "limits":   {"cpu": "500m", "memory": "512Mi"}
  }
' deploy.yaml

# Add an annotation to all matching resources
yq -i 'select(.kind == "Deployment") |
  .metadata.annotations["deploy-time"] = env(DEPLOY_TIME)' k8s/*.yaml

# Extract all image names from a manifest bundle
yq '.spec.template.spec.containers[].image' k8s/*.yaml | sort | uniq

# Generate a summary of all resources
yq 'select(. != null) | .kind + "/" + .metadata.name' k8s/*.yaml
```

### Docker Compose
```bash
# Override a service image tag
yq -i ".services.api.image = \"myapp:${TAG}\"" docker-compose.yml

# Add an environment variable to a service
yq -i '.services.api.environment += ["NEW_VAR=value"]' docker-compose.yml

# Scale replicas for a service
yq -i '.services.worker.deploy.replicas = 4' docker-compose.yml

# Merge base and override compose files (like docker compose -f)
yq '. *+ load("docker-compose.override.yml")' docker-compose.yml
```

### CI/CD Configs
```bash
# GitHub Actions: update a matrix version list
yq -i '.jobs.test.strategy.matrix.node += ["20"]' .github/workflows/ci.yml

# GitLab CI: extract all job names
yq 'keys | .[]' .gitlab-ci.yml

# CircleCI: get all orbs in use
yq '.orbs | to_entries[] | "\(.key): \(.value)"' .circleci/config.yml

# Helm values: override nested values
yq -i '.ingress.hosts[0].host = "api.example.com"' values.yaml
```

### YAML Anchors and Aliases
```bash
# yq resolves anchors by default; to preserve them, use --no-doc-separator
yq --no-doc-separator '.' file-with-anchors.yaml

# Explode/dereference all anchors into full values
yq 'explode(.)' file-with-anchors.yaml

# View anchored values as-is
yq '. | ... comments=""' file.yaml   # Strip comments
```

### Combining with Shell Loops
```bash
# Apply a patch to all YAML files in a directory
for f in k8s/*.yaml; do
  yq -i '.metadata.labels.env = "production"' "$f"
done

# Extract and loop over array values
for svc in $(yq '.services | keys | .[]' docker-compose.yml); do
  echo "Service: $svc"
done

# Validate required fields exist
yq -e '.name and .version and .author' package.yaml || echo "Missing required fields"
```

## Practical Examples

### Daily Config Workflows
```bash
# Quick read
yq '.database.host' config.yaml

# Bump version in package.yaml
yq -i '.version = "2.0.0"' package.yaml

# Extract all keys as env exports
yq '.env | to_entries[] | "export \(.key)=\(.value)"' config.yaml | source

# Pretty-print a JSON API response as YAML
curl -s https://api.example.com/resource | yq -P '.'
```

### Kubernetes Rollout Helper
```bash
# Patch image and apply in one line
yq ".spec.template.spec.containers[0].image = \"myapp:${TAG}\"" deploy.yaml \
  | kubectl apply -f -
```

### Diff Two YAML Files
```bash
diff <(yq -o=json 'sort_keys(..)' a.yaml) <(yq -o=json 'sort_keys(..)' b.yaml)
```

## Chaining with Other Skills

- **jq (cli-jq):** Convert YAML → JSON with `yq -o=json`, pipe to jq for complex queries; or reverse with `yq -o=yaml`
- **kubectl:** `yq` patches manifests, `kubectl apply -f -` consumes them — the classic GitOps combo
- **gh (cli-gh):** Extract workflow/action config values with yq, use gh to trigger workflow runs with the updated params
- **envsubst:** `yq '.' template.yaml | envsubst` for full shell-style `${VAR}` substitution in YAML templates
