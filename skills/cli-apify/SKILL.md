---
name: cli-apify
description: >
  Covers effective use of the Apify CLI for web scraping and
  automation using Actors, datasets, key-value stores, and Crawlee. Covers
  apify init/run/push/login/call/pull, Actor concepts, pagination, proxy
  rotation, scheduling, webhooks, and CSV/JSON export. Activates when the user
  asks about Apify, running or building Actors, cloud web scraping, or
  extracting data at scale.
---

# Apify CLI — Web Scraping & Actor Platform

**Repo:** https://github.com/apify/apify-cli

The Apify CLI manages Actors — containerized scraping/automation tasks that run
locally or on the Apify cloud. Backed by [Crawlee](https://crawlee.dev) for
browser and HTTP crawling. Pairs naturally with Playwright or Puppeteer for
JS-heavy sites.

## When to Activate

**Manual triggers:**
- "How do I use the Apify CLI?"
- "Create / run / deploy an Apify Actor"
- "Scrape a website and export to CSV"
- "Set up pagination / proxy rotation with Apify"

**Auto-detect triggers:**
- User wants scalable, cloud-hosted web scraping
- User wants to schedule a scraper or fire webhooks
- User is building a Crawlee-based crawler
- User needs to store/export large scraping datasets

## Key Commands

### Authentication
```bash
apify login                         # authenticate with token (opens browser)
apify login --token <TOKEN>         # non-interactive (CI/CD)
apify logout
```

### Scaffold & Init
```bash
apify create my-actor               # interactive scaffold (prompts for template)
apify create my-actor --template=playwright-js   # specific template
apify init                          # add .actor/actor.json to existing project
```

### Local Development
```bash
apify run                           # run Actor locally (uses storage/ dir)
apify run --purge                   # clear local storage first, then run
apify run --input='{"url":"https://example.com"}'  # pass inline input
apify run --input=@input.json       # pass input from file
```

### Cloud Operations
```bash
apify push                          # build & deploy Actor to Apify cloud
apify push --version-number=1.2     # deploy as specific version
apify call my-actor                 # run deployed Actor and wait for finish
apify call my-actor --input=@in.json
apify pull my-actor                 # download latest source from cloud
apify actor --version               # print CLI version info
```

### Inspect Outputs
```bash
apify datasets ls                           # list all datasets in your account
apify datasets get-items <datasetId>        # download items as JSON
apify datasets get-items <datasetId> --format=csv > out.csv
apify key-value-stores ls
apify key-value-stores get-record <storeId> <key>
```

## Core Concepts

### Actor Input (`INPUT` key-value record)
```json
// .actor/INPUT_SCHEMA.json defines the schema shown in Apify Console
// Locally, put your input in storage/key_value_stores/default/INPUT.json
{
  "startUrls": [{ "url": "https://example.com" }],
  "maxDepth": 2,
  "proxyConfiguration": { "useApifyProxy": true }
}
```

### Datasets (append-only output)
```typescript
import { Dataset } from 'apify';
await Dataset.pushData({ title: 'Hello', url: 'https://...' });
// Or the global shorthand:
await Actor.pushData({ ... });
```

### Key-Value Stores (arbitrary blobs)
```typescript
await Actor.setValue('result', { items: [...] });           // write
const val = await Actor.getValue('result');                  // read
await Actor.setValue('screenshot.png', buffer, { contentType: 'image/png' });
```

### Request Queue (crawl frontier)
```typescript
const queue = await Actor.openRequestQueue();
await queue.addRequest({ url: 'https://example.com' });
const req = await queue.fetchNextRequest();
await queue.markRequestHandled(req);
```

## Advanced Patterns

### Custom Playwright Scraper (Actor)
```typescript
import { Actor } from 'apify';
import { PlaywrightCrawler } from 'crawlee';

await Actor.init();

const crawler = new PlaywrightCrawler({
  launchContext: { launchOptions: { headless: true } },
  async requestHandler({ page, request, enqueueLinks }) {
    const data = await page.evaluate(() => ({
      title: document.title,
      url:   location.href,
    }));
    await Actor.pushData(data);
    await enqueueLinks();           // follow all links on the page
  },
});

await crawler.run([{ url: 'https://example.com' }]);
await Actor.exit();
```

### Pagination
```typescript
const crawler = new PlaywrightCrawler({
  async requestHandler({ page, request, log }) {
    // scrape current page
    const items = await page.locator('.item').allTextContents();
    await Actor.pushData(items.map(text => ({ text, page: request.url })));

    // enqueue next page if it exists
    const next = await page.locator('a.next-page').getAttribute('href');
    if (next) await crawler.addRequests([next]);
  },
});
```

### Proxy Rotation
```typescript
const proxyConfiguration = await Actor.createProxyConfiguration({
  groups: ['RESIDENTIAL'],   // 'DATACENTER', 'RESIDENTIAL', 'GOOGLE_SERP'
  countryCode: 'US',
});

const crawler = new PlaywrightCrawler({ proxyConfiguration, ... });
```

### Scheduling & Webhooks (cloud)
- Schedule an Actor via Apify Console → Actors → your actor → Schedules tab (cron syntax).
- Webhooks: Console → Actors → Webhooks — fire HTTP POST on `ACTOR.RUN.SUCCEEDED`, `ACTOR.RUN.FAILED`, etc.
- CLI trigger: `apify call my-actor` returns after the run completes; use `--no-wait` for fire-and-forget.

### CSV/JSON Export
```bash
# JSON (default)
apify datasets get-items <id> > results.json

# CSV
apify datasets get-items <id> --format=csv > results.csv

# Filter/transform with jq before saving
apify datasets get-items <id> | jq '[.[] | {title, price: .price | tonumber}]' > clean.json

# Load directly into DuckDB
duckdb -c "SELECT * FROM read_json_auto('results.json') LIMIT 10"
```

### Apify Store (pre-built Actors)
```bash
# Call a public Actor from the store without writing code
apify call apify/web-scraper --input='{"startUrls":[{"url":"https://example.com"}]}'

# Popular store Actors:
#   apify/web-scraper        — universal JS scraper
#   apify/playwright-scraper — Playwright-based
#   apify/cheerio-scraper    — fast HTML-only scraper
#   apify/google-search-scraper
```

## Practical Examples

### Scrape & Export in One Pipeline
```bash
# Run locally, purge old state, pipe dataset to CSV
apify run --purge
apify datasets get-items default --format=csv > output.csv
```

### CI/CD Deployment
```bash
# In GitHub Actions
- run: |
    npm install -g apify-cli
    apify login --token ${{ secrets.APIFY_TOKEN }}
    apify push --version-number=${{ github.run_number }}
```

### Call Actor and Process Results
```bash
# Run cloud Actor, download results, filter with jq
apify call my-actor --input=@input.json
DATASET_ID=$(apify actor --last-run-dataset-id)
apify datasets get-items "$DATASET_ID" | jq '.[] | select(.price < 100)'
```

## Chaining with Other Skills

- **Playwright (cli-playwright):** Playwright is the recommended renderer inside Apify Actors; Apify provides the cloud infrastructure (proxy, scheduling, storage) while Playwright handles DOM interaction.
- **jq:** Pipe `apify datasets get-items` output through jq to filter, reshape, or flatten nested scraping results before saving.
- **DuckDB:** Import exported JSON/CSV directly with `read_json_auto()` / `read_csv_auto()` for SQL analytics on scraped data.
