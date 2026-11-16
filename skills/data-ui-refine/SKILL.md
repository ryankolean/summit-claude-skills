---
name: data-ui-refine
description: >
  Ordered refine passes for any dashboard, admin screen, or data-viewing UI: one
  concern per prompt with a render check between passes (baseline, hierarchy by
  relationship, CTA delight, material fit, progressive disclosure, navigation,
  command palette), then pro passes for numbers, chart choice, color meaning,
  data states, tables and density, accessibility, motion and dark mode, plus a
  26-item AI-slop detector. Use when building or fixing a dashboard, stats page,
  table-heavy screen, admin panel, or any UI where people read data; when the
  user says "fix this slop", "make this dashboard look like a product",
  "refine this UI", "data UI pass", or "Omar's process".
when_to_use: Building or reworking any interface that shows data. Run before calling a dashboard done.
---

# Data UI refine

Source: an observed 7-pass dashboard fix (one prompt per concern, render between
each), extended with professional data-UI practice. Pair with `baseline-ui`
(hard constraints), `design-review` (final audit) and `dataviz` (chart rules);
this skill owns the build order.

**How to run it**
- Start with the slop check (Part C). Two or more tells: run every pass.
- Run passes in order. Pass 8 may run right after pass 1 when the screen is mostly numbers.
- Each pass: send its prompt template (fill the brackets), render, screenshot at 375 / 768 / 1280 in light and dark, then check every item. Fix and re-render until the check passes. Only then start the next pass.
- Log one line per pass in the PR or task: what changed, check result.

**Rules for running it**
- One concern per prompt. Never merge passes; merged passes regress earlier ones.
- Render-check between passes: screenshot at 375 / 768 / 1280, light and dark. A pass is not done until its check passes on the rendered page, not the code.
- Real data only. Seed the UI with realistic values (long names, 7-digit currency, zero rows, negative deltas) before pass 1. Lorem-ipsum dashboards hide every formatting bug.
- Keep a one-line log per pass (what changed, check result). It doubles as the client changelog.

---

## Part A: the 7 passes

### Pass 1: Baseline
**Prompt template**
> Elevate this [dashboard/screen] using professional product-design practice. Constraints: one type scale (max 5 sizes, ratio ~1.2-1.25, e.g. 12/14/16/20/28), max 2 weights; one card style (one radius, one border OR one shadow, not both); neutral palette + one accent used only for the primary action and selection; exactly one primary button per view; spacing on a 4/8px scale. Do not add features, sections, icons, or animation. Change styling only.

**Check (pass if all true)**
- Count of distinct font sizes <= 5; weights <= 2. (Script: collect `getComputedStyle(el).fontSize` across the page.)
- Exactly one element styled as primary button in the viewport.
- Accent color appears only on primary action, selection, focus, and links.
- All cards share one radius and one elevation treatment.
- Squint test: the most important number or action is the first thing you see at 25% zoom.

Sources: Refactoring UI (Wathan & Schoger) chapters on hierarchy, limiting choices, and "establish a type scale"; Material 3 type scale.

### Pass 2: Hierarchy by relationship
**Prompt template**
> Reorganize layout by relationship only. Group elements that are used together (Gestalt proximity: related items closer than unrelated ones). Put page-level actions in the header row, right-aligned. Put KPIs that compare to each other in one row with identical structure (label, value, delta, period). Put detail (tables, lists) below the summary that explains it. Do not restyle; move and group only.

**Check**
- Inner spacing within a group < spacing between groups (measure: group gap >= 2x item gap).
- Page actions live in one place (header), not scattered across cards.
- Every KPI in a row uses the same template and the same period ("vs last 30 days" stated once or per tile, never mixed).
- Reading order (tab order) matches visual order: overview -> drill-down.

Sources: Refactoring UI "spacing between groups"; NN/g dashboards: preattentive attributes (position and length are the strongest quantity encodings; placement implies importance).

### Pass 3: Delight on the primary CTA
**Prompt template**
> Add one micro-interaction to the primary CTA only. On hover/focus, the label changes from the action to the outcome computed from the user's own data (e.g. "Send invoices" -> "Collect $6,420" from the sum of unpaid invoices). Add a small looping icon motion only while hovered. Use transform/opacity only, <= 200ms state change, ease-out, pause on `prefers-reduced-motion: reduce` (keep the label swap, drop the motion). Width must not jump: reserve the wider label's width.

**Check**
- The outcome value is computed from live data, not hardcoded, and formatted per pass 8.
- Works on keyboard focus, not only hover. Touch: outcome shown as a sub-label since there is no hover.
- No layout shift (button width stable; CLS 0 on hover).
- Reduced-motion: label swap still happens, icon loop does not.
- Nothing else on the page animates.

Sources: Apple HIG "Motion" (purposeful, brief, optional under Reduce Motion); `baseline-ui` animation rules; Material 3 motion (emphasized easing, short durations for small components).

### Pass 4: Material / platform fit
**Prompt template**
> Apply a surface treatment that fits the platform: [desktop app: translucent sidebar/toolbars over content (frosted glass); web app: flat layered neutrals with 1px borders; iOS: system materials]. Define it as tokens (surface-0..3, border, blur) and apply consistently to every layer: sidebar, header, cards, popovers, modals, command palette. Glass only on chrome that floats over content, never under dense text or tables. Provide the dark-mode equivalent of every token.

**Check**
- Every surface uses a token; no one-off backgrounds (grep for raw hex/rgba outside the token file).
- Text on translucent layers still meets 4.5:1 against the worst-case content behind it (test with a busy background).
- Dark mode uses elevation (lighter surfaces for higher layers), not inverted light mode.
- `backdrop-filter` limited to small chrome areas (perf: never on full-screen or scrolling surfaces).
- Fallback when `prefers-reduced-transparency: reduce` or no backdrop-filter support: solid surface.

Sources: Apple HIG "Materials"; Material 3 "Elevation" and tonal surfaces; `baseline-ui` (no large blur surfaces).

### Pass 5: Progressive disclosure
**Prompt template**
> Rank every section by how often the user needs it, in the order they do the work (e.g. triage -> act -> review -> configure). Keep the top 1-2 open. Fold the rest into labeled accordions/disclosure rows that show a one-line summary when closed (e.g. "Payouts: 3 pending, next on Nov 20"). Persist open/closed state per user. Do not delete content.

**Check**
- Above the fold answers the user's first question of the session without interaction.
- Every collapsed section shows a summary value, so collapsing never hides an alert.
- Alerts/errors inside a collapsed section surface on its header (badge/count).
- Disclosure controls are buttons with `aria-expanded`, keyboard operable.
- No more than 2 levels of nesting.

Sources: NN/g "Progressive Disclosure" (defer advanced/rare features; what is on the initial screen signals importance).

### Pass 6: Navigation
**Prompt template**
> Restructure navigation: group related destinations under short group labels; give every kept item an icon from one icon set at one size and stroke; remove items used less than [monthly]; move Settings, Help, and account to the bottom of the sidebar (or a user menu). Mark the current location. Max ~7 items per group.

**Check**
- One icon family, one size, one stroke weight; icons never replace labels (labels visible in expanded nav; tooltips when collapsed).
- Current page has a visible selected state that is not color-only (weight, indicator bar, or background).
- Settings/help are visually demoted (bottom or menu).
- URL reflects location; back button works; deep links land on the right tab/filter.
- Nav collapses to a usable pattern at 375 (drawer or bottom bar), no horizontal scroll.

Sources: NN/g navigation/IA guidance (labels over icons alone); Apple HIG "Sidebars"; Atlassian Design "Navigation system"; `design-review` "Navigation as Wayfinding".

### Pass 7: Command palette
**Prompt template**
> Replace the search box with a compact Cmd+K (Ctrl+K on Windows/Linux) trigger showing the shortcut hint. The palette opens a dialog with: search across records and pages, a "Quick actions" group (the 5 most common actions with their keyboard shortcuts shown right-aligned), and recent items. Use an accessible combobox/dialog primitive (cmdk, Radix, React Aria). Escape closes and returns focus to the trigger.

**Check**
- Opens with Cmd+K and Ctrl+K and by click; trigger is discoverable (visible hint, not shortcut-only).
- Focus trapped in dialog; arrow keys move selection; Enter runs; Escape closes and restores focus.
- Every listed shortcut actually works outside the palette.
- Shortcuts do not hijack browser/OS defaults or fire while typing in inputs.
- Screen reader announces result count (`aria-live`).

Sources: WAI-ARIA APG combobox and dialog patterns; Superhuman/Linear palette convention; Apple HIG "Keyboards" (don't override system shortcuts).

---

## Part B: pro additions (passes 8-14)

The 7 passes make a dashboard look intentional. These make it **correct and trustworthy**, which is what professional data-UI teams spend most of their time on. Run them after pass 7, same one-concern rule. Pass 8 can also run right after pass 1 if the data is the product.

### Pass 8: Numbers
**Prompt template**
> Audit every number on the page. Format with `Intl.NumberFormat`/`Intl.DateTimeFormat` using the user's locale. Rules: tabular figures on any number that updates or sits in a column; right-align numeric columns and their headers; consistent precision per column; compact notation only in KPI tiles with the exact value in a tooltip/title; currency symbol and unit stated once (header or tile label), not repeated per cell when the column is single-currency; negative values with a minus sign (or accounting parentheses for finance) plus a non-color cue; deltas state the comparison period; percentages vs percentage points distinguished.

**Check**
- `font-variant-numeric: tabular-nums` on all numeric cells, KPIs, timers, counters.
- Numeric columns and headers right-aligned; nominal numbers (IDs, ZIPs, phone, invoice #) left-aligned.
- No `toFixed` string-building for display; all via Intl (grep).
- Same column = same decimals. 0 is rendered as 0 (or an explicit dash with legend), never blank.
- Every delta has direction icon + sign + period, so it reads without color.
- Dates: relative ("2h ago") only for recent events, with absolute timestamp on hover; timezone stated where it matters.

Sources: Carbon Data table usage (right-align variable numeric values and their headers; left-align discrete numbers like ports/ZIPs); Refactoring UI "use tabular figures / align numbers right"; Few, *Show Me the Numbers* (table design, precision); MDN `Intl.NumberFormat`.

### Pass 9: Chart choice and data-ink
**Prompt template**
> For each chart, state the question it answers in one sentence and pick the form that answers it: change over time -> line (bars for few discrete periods); compare categories -> sorted horizontal bar; part-to-whole -> stacked bar or a single number (pie only for 2-3 parts); distribution -> histogram/box; correlation -> scatter; single KPI trend -> sparkline beside the number. Then maximize data-ink: remove 3D, gradients, drop shadows, heavy gridlines, redundant legends (label lines directly), and decorative chart borders. Bars start at zero. Use the `dataviz` skill palette.

**Check**
- Each chart has a title that is the question or the takeaway, axis units, and a source/period.
- No pie/donut with > 3 slices; no dual-axis charts unless both scales are labeled and unavoidable; no 3D.
- Bar axes start at 0; line axes may not, but say so.
- Direct labels replace legends where <= 4 series.
- Gridlines light or removed; no chart border; no chart where a number would do (a "chart" of one value is a KPI).
- Tooltip shows exact formatted value + period; keyboard-reachable or a data-table alternative exists.

Sources: Tufte, *The Visual Display of Quantitative Information* (data-ink ratio, chartjunk); Few, *Information Dashboard Design* (dashboard = single screen, at-a-glance monitoring; avoid gauges and decoration); Cleveland & McGill (position/length most accurate encodings); NN/g "Dashboards: Making Charts and Graphs Easier to Understand"; Polaris data visualization guidance (clear labels, unobtrusive axes, color with specific meaning; page under rework, check live); local `dataviz` skill.

### Pass 10: Color for meaning only
**Prompt template**
> Audit every color. Neutrals for structure; one accent for interaction; semantic colors (success/warning/critical/info) only for status; categorical chart palette only in charts. Remove every color used for decoration. Status never relies on color alone: add icon, text, or pattern. Check all pairs for contrast in light and dark.

**Check**
- Body text >= 4.5:1, large text and UI components/graph objects >= 3:1 (WCAG 2.2 1.4.3, 1.4.11).
- Red/green pairs always carry a second cue; simulate deuteranopia.
- Semantic colors are never reused as categories in charts (a green series must not mean "good" unless it does).
- Accent count per view = 1.
- Chart series colors pass a CVD-safe check (`dataviz` validator).

Sources: Atlassian Design "Data visualization color" (brand color for single series; categorical tokens in order; don't rely on color alone, add shapes/patterns/direct labels); WCAG 2.2; Carbon data-viz color palettes.

### Pass 11: Data states
**Prompt template**
> Design every state for every data region: loading (skeleton matching final layout), empty-first-use (explain what will appear + one action to make it appear), empty-filtered (say which filter caused it + clear filters), error (what failed, whether data shown is stale, retry), partial (some sources failed: show what loaded and flag the gap), stale (last-updated time; warn past threshold), and permission-denied. Add a dev toggle or story for each.

**Check**
- Each region has all 7 states reachable via a toggle/Storybook story and screenshotted.
- Skeleton dimensions match final content (no layout shift on load; CLS < 0.1). No skeleton for loads < ~1s (show nothing, then content).
- Empty state has exactly one primary next action.
- Error copy says what happened and what to do; never a raw stack or "Something went wrong" alone.
- "Last updated" visible on any data that is not live.

Sources: NN/g "Skeleton Screens 101" (match layout; unnecessary under 1s; not a substitute for performance); NN/g "Designing Empty States in Complex Applications"; Carbon "Empty states" and "Loading" patterns; `baseline-ui` (empty state one action, errors next to the action).

### Pass 12: Tables and density
**Prompt template**
> Make every table production-grade: sticky header, sortable columns with visible sort direction, column widths fit content type, row height from a density token (compact 32px / default 40px / comfortable 48px) with a user toggle that persists, text truncation with full value on hover/focus, row actions on hover AND via a visible kebab for touch/keyboard, bulk selection with a count bar, pagination or virtualization over ~100 rows. On narrow screens: pin the identifier column and scroll the rest horizontally inside the table container, or switch to stacked label/value rows. The page itself must never scroll horizontally.

**Check**
- At 375: `document.documentElement.scrollWidth === clientWidth`; table scrolls inside its container with the key column pinned.
- Density toggle changes row height only via tokens; text sizes stay >= 12px in compact.
- Sort state exposed via `aria-sort`; header is a real `<th>` with `scope`.
- Truncated cells reveal full value to keyboard users.
- Hover-only affordances have a non-hover equivalent.

Sources: Carbon Data table (sizes xs-xl, toolbar, batch actions, expandable rows); Material 3 density guidance; Atlassian Dynamic table; Polaris IndexTable (bulk actions, condensed on mobile).

### Pass 13: Accessibility and focus
**Prompt template**
> Keyboard-walk the whole screen. Every interactive element reachable in visual order with a visible focus indicator (2px+, 3:1 against adjacent colors, not removed by `outline: none`). Charts get a text summary and an accessible data table toggle. Live-updating numbers use polite announcements only for meaningful changes. Hit targets >= 24x24 CSS px (44 on touch-first).

**Check**
- Full keyboard pass completes the primary task with no mouse.
- `:focus-visible` styles present on every control (axe + manual).
- axe-core: 0 serious/critical.
- Each chart has an accessible name, description, and data alternative.
- Respect `prefers-reduced-motion`, `prefers-contrast`, `prefers-reduced-transparency`.

Sources: WCAG 2.2 (2.4.7 Focus Visible, 2.4.11 Focus Not Obscured, 2.5.8 Target Size Minimum); WAI-ARIA APG; Carbon accessibility for data table.

### Pass 14: Motion restraint and dark-mode parity (final sweep)
**Prompt template**
> Remove every animation that does not show a state change, spatial relationship, or the pass-3 CTA. Number tickers, staggered card entrances, and chart draw-ins on every load go. Then render the whole screen in dark mode and fix every token that fails contrast or loses hierarchy.

**Check**
- Animations on page load: 0 (except skeleton shimmer, which also stops under reduced motion).
- Remaining transitions <= 200ms for feedback, transform/opacity only, no `transition: all`.
- Dark mode: every screenshot from passes 1-13 re-taken in dark; no pure #000 surfaces under text, no pure #FFF body text on dark (use off-white), accent desaturated, charts re-validated.
- Light/dark parity: no component exists in only one theme.

Sources: Material 3 motion; Apple HIG "Dark Mode"; `design-review` color items (dark mode elevation, off-white text).

### Per-pass checks to bolt onto the original 7
| Pass | Add this check |
|---|---|
| 1 | Run pass 8 numeric checks immediately if the screen is mostly numbers. |
| 2 | Every metric answers "compared to what?" (target, prior period, or benchmark). Few: a number without context is not information. |
| 3 | The CTA outcome must be honest: if the sum is $0, show the plain action label, never "Collect $0". |
| 4 | Glass never behind tables or charts. |
| 5 | Collapsed sections leak their alerts (badge). |
| 6 | Shareable URLs for every view, filter, and sort. |
| 7 | The palette is an accelerator, not the only path: every action also exists in visible UI. |

---

## Part C: slop tells (AI-default UI detector)

Flag any of these on a dashboard. Two or more = redo pass 1 with the tells listed as explicit bans.

**Color and surface**
1. Purple/indigo/violet gradients, blue-to-purple anything, gradient text on headings or numbers.
2. Glowing stat cards: colored outer glow, neon borders, or a colored shadow under KPI tiles.
3. Every card a different pastel tint, or each KPI in its own accent color with no meaning.
4. Glassmorphism everywhere, including behind tables and body text.
5. Dark navy (#0F172A-ish) background + cyan/purple accent "cyber" default.
6. Same `rgba(0,0,0,.1)` soft shadow and the same large radius on every element.

**Layout**
7. Card mosaic: everything chopped into equal rounded cards, including things that are not objects (a page title in a card).
8. Four identical KPI tiles across the top with big number, tiny label, and a green "+12.5%" pill, regardless of whether those 4 numbers matter.
9. Icon-in-a-colored-circle on every tile.
10. Colored left border stripe on cards.
11. Centered text in data contexts (centered table cells, centered numbers).
12. Decorative charts: a sparkline or area chart with no axis, no period, no value, filling space.

**Content and copy**
13. Emoji welcome banner ("Welcome back, Alex!" + waving-hand emoji) or emoji as icons/bullets.
14. Generic greeting + date header taking the most prominent position instead of the most important number.
15. Fake-precise or round fake data ($12,345.67, 1,234 users, 98.5% uptime) and identical trend shapes on every chart.
16. "Insights" panels with vague AI-ish copy ("Your revenue is trending positively!").
17. Tracked-out ALL-CAPS eyebrow labels over every section; middle-dot meta strings ("Today · 3 tasks · 2 alerts"); "→" appended to every link.
18. Buttons labeled "Get started", "Explore", "Learn more" inside an app.

**Data and interaction**
19. Proportional (non-tabular) figures that jitter as numbers update; left-aligned numeric columns.
20. Donut chart with 6+ slices and a legend; 3D or gradient-filled bars.
21. Red/green as the only signal of good/bad.
22. Spinners everywhere instead of skeletons; no empty or error states at all (only the happy path was built).
23. Count-up number animations and staggered fade-up entrances on every load.
24. Search bar + bell + avatar header cluster that does nothing; a command palette that is only search.
25. Toggle for dark mode but dark mode is an inverted afterthought with failed contrast.
26. `system-ui`/Inter default stack with no type scale (fine as a choice, a tell as a default; see `design-review` item 11).

---

## Sources
- Wathan & Schoger, *Refactoring UI* (2018): hierarchy, limiting choices, type scale, tabular figures, spacing groups. https://www.refactoringui.com/
- Tufte, *The Visual Display of Quantitative Information* (2nd ed., 2001): data-ink ratio, chartjunk.
- Few, *Information Dashboard Design* (2nd ed., 2013) and *Show Me the Numbers* (2012): dashboard definition, table and number design, chart choice.
- Cleveland & McGill, "Graphical Perception" (JASA, 1984): encoding accuracy ranking.
- NN/g: Dashboards and preattentive attributes https://www.nngroup.com/articles/dashboards-preattentive/ ; Skeleton Screens 101 https://www.nngroup.com/articles/skeleton-screens/ ; Progressive Disclosure https://www.nngroup.com/articles/progressive-disclosure/ ; Empty states in complex apps https://www.nngroup.com/articles/empty-state-interface-design/
- IBM Carbon Data table usage (numeric alignment, sizes, batch actions) https://carbondesignsystem.com/components/data-table/usage/
- Atlassian Design, Data visualization color https://atlassian.design/foundations/color/data-visualization-color
- Shopify Polaris, Data visualizations https://polaris.shopify.com/design/data-visualizations (page marked as under rework for v12; confirm live content before quoting)
- Material Design 3: type scale, elevation, density, motion https://m3.material.io/
- Apple HIG: Materials, Motion, Dark Mode, Sidebars, Keyboards https://developer.apple.com/design/human-interface-guidelines/
- WCAG 2.2 https://www.w3.org/TR/WCAG22/ ; WAI-ARIA APG (combobox, dialog, table) https://www.w3.org/WAI/ARIA/apg/
- Local: `~/.claude/skills/baseline-ui/SKILL.md`, `~/.claude/skills/design-review/SKILL.md` (App UI rules, slop blacklist), `~/.claude/skills/ui-ux-pro-max/SKILL.md`, frontend-design plugin skill, `dataviz` skill.
