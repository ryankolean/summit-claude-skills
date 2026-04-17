---
name: cli-playwright
description: >
  Covers effective use of Playwright for browser automation and
  testing. Covers CLI commands (codegen, test, show-report, screenshot, pdf),
  the core API (goto, click, fill, locator, waitForSelector, evaluate), and
  advanced patterns like visual regression, trace viewer, mobile emulation,
  network interception, and auth handling. Activates when the user asks about
  Playwright, browser automation, end-to-end testing, or web scraping with a
  real browser.
---

# Playwright — Browser Automation & Testing

**Repo:** https://github.com/microsoft/playwright

Playwright drives Chromium, Firefox, and WebKit from Node.js (or Python/Java/.NET).
Use it for end-to-end tests, scraping, screenshots, PDFs, and any workflow that
requires a real browser with JavaScript execution.

## When to Activate

**Manual triggers:**
- "How do I use Playwright?"
- "Write a Playwright test"
- "Take a screenshot / generate a PDF with a browser"
- "Intercept network requests in a test"

**Auto-detect triggers:**
- User wants end-to-end browser tests
- User needs to scrape a JS-heavy site
- User asks about visual regression testing
- User wants to record a browser interaction

## Key Commands

### Install & Setup
```bash
npm init playwright@latest          # scaffold new project (installs browsers too)
npx playwright install              # install/update all browsers
npx playwright install chromium     # install only Chromium
npx playwright install --with-deps  # also install OS dependencies (CI)
```

### Run Tests
```bash
npx playwright test                          # run all tests
npx playwright test tests/login.spec.ts      # run a specific file
npx playwright test --grep "checkout"        # run tests matching pattern
npx playwright test --project=chromium       # run in one browser only
npx playwright test --headed                 # show browser window
npx playwright test --ui                     # open interactive UI mode
npx playwright test --debug                  # open Playwright Inspector
npx playwright test --workers=4              # parallel workers
npx playwright test --retries=2              # retry flaky tests
```

### Code Generation
```bash
npx playwright codegen https://example.com          # record actions → test code
npx playwright codegen --device="iPhone 13" URL     # record with mobile emulation
npx playwright codegen --save-storage=auth.json URL # record and save auth state
```

### Reporting
```bash
npx playwright show-report                  # open last HTML report in browser
npx playwright show-report ./my-report      # open report from specific path
npx playwright show-trace trace.zip         # open a trace archive
```

### Screenshots & PDFs (CLI one-liners)
```bash
npx playwright screenshot https://example.com shot.png
npx playwright screenshot --full-page https://example.com full.png
npx playwright pdf https://example.com page.pdf
```

## Core API

### Page Navigation & Interaction
```typescript
import { chromium } from '@playwright/test';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

await page.goto('https://example.com');               // navigate
await page.goto('https://example.com', { waitUntil: 'networkidle' });

await page.click('text=Sign in');                     // click by text
await page.fill('#email', 'user@example.com');        // fill input
await page.press('#password', 'Enter');               // key press
await page.selectOption('select#country', 'US');      // select dropdown
await page.check('#agree');                           // check checkbox
await page.hover('.menu-item');                       // hover

await page.waitForSelector('.dashboard');             // wait for element
await page.waitForLoadState('networkidle');           // wait for network quiet
await page.waitForURL('**/dashboard');                // wait for URL change
```

### Locators (preferred over selectors)
```typescript
// Locators are auto-waiting and retry-able
const btn = page.locator('button[type=submit]');
const byText = page.getByText('Continue');
const byRole = page.getByRole('button', { name: 'Submit' });
const byLabel = page.getByLabel('Email address');
const byPlaceholder = page.getByPlaceholder('Search...');
const byTestId = page.getByTestId('login-btn');  // data-testid attribute

await btn.click();
await byLabel.fill('hello@world.com');
await expect(byRole).toBeEnabled();
```

### Assertions (test mode)
```typescript
import { expect } from '@playwright/test';

await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle('Dashboard');
await expect(page.locator('h1')).toHaveText('Welcome');
await expect(page.locator('.alert')).toBeVisible();
await expect(page.locator('input')).toBeEnabled();
await expect(page.locator('img')).toHaveAttribute('src', /avatar/);
```

### Screenshots & PDFs (API)
```typescript
await page.screenshot({ path: 'shot.png' });
await page.screenshot({ path: 'full.png', fullPage: true });
await page.locator('.chart').screenshot({ path: 'chart.png' });
await page.pdf({ path: 'page.pdf', format: 'A4' });
```

### JavaScript Evaluation
```typescript
const title = await page.evaluate(() => document.title);
const links = await page.evaluate(() =>
  Array.from(document.querySelectorAll('a')).map(a => a.href)
);
await page.evaluate((val) => { window.localStorage.setItem('key', val); }, 'hello');
```

## Advanced Patterns

### Visual Regression Testing
```typescript
// First run creates baseline snapshots; subsequent runs diff against them
await expect(page).toHaveScreenshot('home.png');
await expect(page.locator('.hero')).toHaveScreenshot('hero.png', {
  maxDiffPixelRatio: 0.01,   // allow 1% pixel difference
});
// Update snapshots: npx playwright test --update-snapshots
```

### Parallel Tests
```typescript
// playwright.config.ts
export default {
  workers: process.env.CI ? 2 : undefined,  // auto on local, limited on CI
  fullyParallel: true,                       // tests within a file run in parallel
};
```

### Trace Viewer
```typescript
// playwright.config.ts — record traces on failure
use: {
  trace: 'on-first-retry',   // 'on', 'off', 'retain-on-failure'
}
// Inspect: npx playwright show-trace trace.zip
```

### Mobile Emulation
```typescript
import { devices } from '@playwright/test';

// playwright.config.ts
projects: [
  { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
  { name: 'Mobile Safari', use: { ...devices['iPhone 13'] } },
],
```

### Network Interception
```typescript
// Block images and fonts to speed up tests
await page.route('**/*.{png,jpg,jpeg,gif,svg,woff,woff2}', r => r.abort());

// Mock an API response
await page.route('**/api/users', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Alice' }]),
  });
});

// Intercept and modify a request
await page.route('**/api/search', async route => {
  const req = route.request();
  await route.continue({ headers: { ...req.headers(), 'X-Custom': 'value' } });
});
```

### Auth Handling (reuse sessions)
```typescript
// Save auth state after login
const page = await browser.newPage();
await page.goto('/login');
await page.fill('#user', 'admin');
await page.fill('#pass', 'secret');
await page.click('[type=submit]');
await page.context().storageState({ path: 'auth.json' });

// playwright.config.ts — reuse state for all tests
use: { storageState: 'auth.json' }
```

### Request/Response Logging
```typescript
page.on('request',  req  => console.log('>>', req.method(), req.url()));
page.on('response', resp => console.log('<<', resp.status(), resp.url()));
page.on('console',  msg  => console.log('BROWSER:', msg.text()));
```

## Practical Examples

### Scrape a Table to JSON
```typescript
const rows = await page.locator('table tbody tr').evaluateAll(trs =>
  trs.map(tr => ({
    name:  tr.cells[0].textContent?.trim(),
    price: tr.cells[1].textContent?.trim(),
  }))
);
console.log(JSON.stringify(rows, null, 2));
```

### Download a File
```typescript
const [download] = await Promise.all([
  page.waitForEvent('download'),
  page.click('a[href$=".csv"]'),
]);
await download.saveAs('./data.csv');
```

### Handle Dialogs
```typescript
page.on('dialog', dialog => dialog.accept());  // auto-dismiss all dialogs
```

### Paginate and Collect Data
```typescript
const results = [];
while (true) {
  const items = await page.locator('.item').allTextContents();
  results.push(...items);
  const next = page.locator('a.next');
  if (!(await next.isVisible())) break;
  await next.click();
  await page.waitForLoadState('networkidle');
}
```

## Chaining with Other Skills

- **Apify (cli-apify):** Use Playwright inside an Apify Actor for cloud-scale scraping with proxy rotation and scheduling; Playwright handles rendering, Apify handles infrastructure.
- **jq:** Pipe `page.evaluate()` JSON output to jq for filtering — `node scrape.js | jq '.[] | select(.price < 50)'`.
- **fzf (cli-fzf):** Pipe test names from `npx playwright test --list` into fzf to interactively pick which test to run.
