---
name: cli-httpie
description: >
  Covers effective use of HTTPie (http/https commands) for making
  HTTP requests from the terminal. Activates when the user asks about HTTPie,
  testing REST APIs from the command line, sending JSON bodies, managing auth
  tokens, or debugging HTTP requests interactively.
---

# HTTPie — Human-Friendly HTTP Client

**Repo:** https://github.com/httpie/cli

Modern, user-friendly HTTP client for the terminal. Designed for interacting
with REST APIs, web services, and HTTP servers. Produces colorized, formatted
output by default. Uses an intuitive syntax for JSON bodies, headers, query
params, and auth — no `--data-urlencode` or `-H "Content-Type: application/json"` required.

## When to Activate

**Manual triggers:**
- "How do I use HTTPie?"
- "Test this REST API from the terminal"
- "Send a POST with a JSON body"
- "Make an authenticated API call"

**Auto-detect triggers:**
- User wants to send HTTP requests from the terminal and prefers readable syntax
- User needs session persistence or cookie handling for API workflows
- User is debugging HTTP headers, status codes, or request/response bodies
- User wants to pipe API responses to jq for processing
- User needs to upload files or submit forms from the terminal

## Key Commands

### Installation and Basics
```bash
# Install
brew install httpie          # macOS
pip install httpie           # Python (all platforms)
apt install httpie           # Debian/Ubuntu

# Commands
http GET https://api.example.com/users      # Default: GET
https api.example.com/users                 # 'https' alias always uses HTTPS
http POST api.example.com/users             # POST
http PATCH api.example.com/users/1
http PUT api.example.com/users/1
http DELETE api.example.com/users/1
http HEAD api.example.com
http OPTIONS api.example.com
```

### Item Types (the core syntax)
```bash
# JSON fields (default when any json-like item is present)
http POST api.example.com/users name=Alice age:=30 active:=true

# String value:       key=value
# Non-string value:   key:=json_value   (number, bool, array, object)
# Header:             Key:Value
# Query parameter:    param==value
# File upload:        field@/path/to/file

# Examples
http POST api.example.com/items \
  name="My Item" \
  price:=9.99 \
  tags:='["sale","new"]' \
  metadata:='{"color":"red"}' \
  Authorization:"Bearer $TOKEN" \
  page==1 \
  limit==50
```

### GET with Query Parameters
```bash
http GET api.example.com/search q==hello lang==en page==2
# → GET /search?q=hello&lang=en&page=2

https httpbin.org/get foo==bar baz==qux
```

### POST with JSON Body
```bash
# Explicit JSON
http POST api.example.com/users \
  name="Alice" \
  email="alice@example.com" \
  age:=28 \
  roles:='["admin","user"]'

# From a file
http POST api.example.com/data < payload.json

# Echo stdin (pipe JSON directly)
echo '{"name":"Alice"}' | http POST api.example.com/users

# From file with @
http POST api.example.com/data Content-Type:application/json @payload.json
```

### Headers
```bash
http GET api.example.com \
  Authorization:"Bearer $TOKEN" \
  Accept:application/json \
  X-Request-ID:abc123

# Print request and response headers only (no body)
http --headers GET api.example.com
```

### Output Control
```bash
http --print=HhBb api.example.com   # Print: request Headers, response Headers, req Body, resp Body
http --print=b api.example.com      # Response body only (default for piping)
http --headers api.example.com      # Response headers only
http --body api.example.com         # Response body only (explicit)
http -v api.example.com             # Verbose: everything (equivalent to --print=HhBb)
http --quiet api.example.com        # Suppress all output
http --stream api.example.com       # Stream the response (SSE, chunked)
http -o output.json api.example.com # Save body to file
http --download api.example.com/file.zip  # Download with progress bar
```

### Authentication
```bash
# Basic auth
http -a username:password api.example.com

# Bearer token
http api.example.com Authorization:"Bearer $TOKEN"

# Digest auth
http --auth-type=digest -a user:pass api.example.com

# API key as header
http api.example.com X-API-Key:$API_KEY

# API key as query param
http api.example.com apikey==$API_KEY
```

### Sessions (Persistent Cookies + Auth)
```bash
# Create/reuse a named session (stored in ~/.config/httpie/sessions/)
http --session=myapi POST api.example.com/login username=me password=secret
# Subsequent requests reuse cookies and auth from the session
http --session=myapi GET api.example.com/protected-endpoint

# Anonymous session (temp file path)
http --session=/tmp/mysession.json GET api.example.com

# Session with Bearer token persistence
http --session=github Authorization:"Bearer $GH_TOKEN" GET api.github.com/user
# Now this works without the header:
http --session=github GET api.github.com/repos
```

### Forms and File Uploads
```bash
# URL-encoded form (not JSON)
http --form POST api.example.com/login username=me password=secret

# Multipart file upload
http --multipart POST api.example.com/upload photo@/path/to/photo.jpg

# Multiple files
http --multipart POST api.example.com/batch \
  file1@/tmp/a.csv \
  file2@/tmp/b.csv

# Form field + file
http --multipart POST api.example.com/submit \
  name="My Upload" \
  attachment@./report.pdf
```

### Downloads
```bash
http --download api.example.com/archive.tar.gz
http --download -o custom-name.tar.gz api.example.com/archive.tar.gz
http --download api.example.com/file.zip --continue  # Resume interrupted download
```

## Advanced Patterns

### Session Persistence with Auth Tokens
```bash
# Login, capture token, reuse in session
TOKEN=$(http POST api.example.com/auth/login \
  username=me password=secret \
  | jq -r '.token')

# Store token in session
http --session=myapp \
  Authorization:"Bearer $TOKEN" \
  GET api.example.com/profile

# All subsequent calls use the session
http --session=myapp GET api.example.com/dashboard
http --session=myapp POST api.example.com/posts title="Hello"
```

### Piping with jq
```bash
# Basic pipe to jq
http GET api.example.com/users | jq '.[] | .email'

# Filter active users and extract name
http GET api.example.com/users | jq '[.[] | select(.active)] | map(.name)'

# POST and inspect the response
http POST api.example.com/items name="Widget" price:=9.99 \
  | jq '{id: .id, created: .created_at}'

# Chain: create user, then use their ID in next request
USER_ID=$(http POST api.example.com/users name="Alice" | jq -r '.id')
http POST api.example.com/users/$USER_ID/activate
```

### SSL and Proxy
```bash
# Ignore SSL certificate verification (dev only)
http --verify=no GET https://localhost:8443/api

# Use a custom CA bundle
http --verify=/path/to/ca-bundle.crt GET https://internal.corp/api

# Use a client certificate
http --cert=client.crt --cert-key=client.key GET https://api.example.com

# Route through a proxy
http --proxy=http:http://proxy:8080 GET api.example.com

# SOCKS proxy
http --proxy=all:socks5://localhost:1080 GET api.example.com
```

### Debugging
```bash
# Full request + response (headers and body)
http -v POST api.example.com/data name=test

# Print only what you need (H=req headers, h=resp headers, B=req body, b=resp body)
http --print=Hh api.example.com     # Just headers
http --print=b api.example.com      # Just response body

# Offline mode: print what the request would look like without sending
http --offline POST api.example.com/data name=Alice

# Follow redirects (default: on) or disable
http --follow GET api.example.com/redirect
http --no-follow GET api.example.com/redirect

# Show timing info
http --meta api.example.com
```

### Environment Variables with .env Files
```bash
# HTTPie reads .env in current directory automatically
# .env file:
# API_URL=https://api.example.com
# TOKEN=mytoken

http GET $API_URL/users Authorization:"Bearer $TOKEN"
```

### Default Options (Config)
```bash
# ~/.config/httpie/config.json
{
  "default_options": [
    "--session=default",
    "--timeout=30"
  ]
}
```

### Streaming and SSE
```bash
# Server-sent events or chunked responses
http --stream GET api.example.com/events

# Watch a log endpoint
http --stream GET api.example.com/logs/tail | grep ERROR
```

## Practical Examples

### API Development Workflow
```bash
# Quickly test a local API
http POST localhost:8080/api/users name="Test User" email="test@example.com"

# Check health endpoint
http GET localhost:8080/health

# Test pagination
http GET localhost:8080/items page==1 per_page==10
http GET localhost:8080/items page==2 per_page==10
```

### GitHub API via HTTPie
```bash
# Authenticate with gh token
TOKEN=$(gh auth token)

# List your repos
http GET api.github.com/user/repos \
  Authorization:"Bearer $TOKEN" \
  per_page==5 \
  | jq '.[].full_name'

# Create an issue
http POST api.github.com/repos/owner/repo/issues \
  Authorization:"Bearer $TOKEN" \
  title="Bug report" \
  body="Steps to reproduce..."
```

### Upload and Process a File
```bash
# Upload CSV and get JSON response
http --multipart POST api.example.com/import data@report.csv \
  | jq '{imported: .count, errors: .errors}'
```

### One-liner OAuth Flow Debug
```bash
# Exchange auth code for token (verbose to see full exchange)
http -v POST oauth.example.com/token \
  --form \
  grant_type=authorization_code \
  code=$AUTH_CODE \
  client_id=$CLIENT_ID \
  client_secret=$CLIENT_SECRET \
  redirect_uri=https://myapp.com/callback
```

## Chaining with Other Skills

- **jq (cli-jq):** HTTPie pipes beautifully to jq — use `http GET url | jq '.field'` as the standard API exploration pattern
- **gh (cli-gh):** Use `gh auth token` to get a GitHub token, then pass it to HTTPie for raw GitHub API calls beyond what gh supports
- **yq (cli-yq):** For APIs returning YAML (rare but possible), pipe HTTPie output to yq for processing
- **fzf (cli-fzf):** Combine HTTPie + jq to get a list of resources, then fzf for interactive selection before a follow-up request
