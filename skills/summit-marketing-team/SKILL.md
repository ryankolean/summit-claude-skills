---
name: summit-marketing-team
description: Reusable 6-role marketing prompt framework for Summit. Treats Claude as a six-role functional marketing team (Market Researcher, Brand Strategist, Content Strategist, Copywriter, Growth Analyst, Repurposing Engine) wired by a System Flow and structured via the Operator Prompting formula (Role/Context/Objective/Task/Output). Activate when user says "marketing team", "run marketing flow", "act as [role-name]", "research the audience", "find positioning", "build content pillars", "write hooks/scripts", "analyze post performance", "repurpose this content", or asks for any structured marketing artifact (pain-desire map, positioning statement, content pillars, hooks, repurposed assets).
---

# summit-marketing-team

Six specialized marketing role prompts plus a System Flow that orchestrates them. Replaces ad-hoc single-prompt marketing dumps with a reusable pipeline.

## When to use

- User wants any of: audience research, brand positioning, content strategy, copywriting (hooks/scripts/CTAs), post-performance analysis, content repurposing.
- User invokes a single role ("act as the brand strategist on this offer") OR runs the full pipeline ("run the marketing flow on summit's freedom-at-45 mini-app").
- User wants Operator Prompting formula applied to a marketing request.

If the request is non-marketing, exit and route elsewhere.

## The 6 roles

Each role lives in `references/`. Load only the role(s) needed for the current task — do not pre-load all six.

| Role | File | Objective |
|---|---|---|
| 1. Market Researcher | `references/role-1-market-researcher.md` | Eliminate audience guessing |
| 2. Brand Strategist | `references/role-2-brand-strategist.md` | Stand out or disappear |
| 3. Content Strategist | `references/role-3-content-strategist.md` | Remove random posting |
| 4. Copywriter | `references/role-4-copywriter.md` | Stop scroll + drive action |
| 5. Growth Analyst | `references/role-5-growth-analyst.md` | Improve, not guess |
| 6. Repurposing Engine | `references/role-6-repurposing-engine.md` | Multiply output without burnout |

Each role file contains: objective, required inputs, questions to ask, deliverables, and a ready-to-paste prompt body.

## System Flow

```
Research → Strategy → Content → Distribution → Analysis → (loop)
   (1)        (2)        (3)         (4)            (5)
```

Role 6 (Repurposing) attaches at the Distribution stage to multiply outputs across formats.

**Meta-prompt: "Run the marketing flow."** Sequence:

1. Run Role 1 on the supplied audience inputs → produces Pain-Desire Map, Objection List, Language Bank.
2. Feed Role 1 output + offer into Role 2 → produces Positioning Statements, Domination Angle, Brand Voice Rules.
3. Feed Roles 1+2 output into Role 3 → produces Content Pillars, 30 Strategic Ideas, Weekly Plan.
4. Feed Roles 1+2+3 into Role 4 → produces Hooks, Scripts, CTAs.
5. After publishing, feed performance data into Role 5 → produces Improvement Report, Next 10 Experiments.
6. Whenever an asset is proven (Role 5 confirms), pass it through Role 6 → produces platform-native variants.

Output of each stage feeds the next. Never run a downstream role without its upstream inputs — flag missing inputs and ask the user to supply them.

## Operator Prompting formula

Every request to any role follows this 5-part structure. Use it whether the user invokes one role or the full flow.

| Part | Definition | Example |
|---|---|---|
| **Role** | Which of the 6 personas to embody | "Act as the Content Strategist." |
| **Context** | Audience, offer, prior outputs, data | "Audience: small-firm CPAs. Offer: 90-day automation sprint. Prior: pain points attached." |
| **Objective** | Precise business outcome | "Lift saved-post rate above 4% on Instagram." |
| **Task** | Specific action to perform | "Generate 3-5 content pillars + 30 angles mapped to awareness stages." |
| **Output** | Desired structured format | "Markdown table: pillar | stage | angle | hook seed | CTA direction." |

Compressed example:
> "Act as the Content Strategist. Audience + offer attached. Goal: lift saved-post rate >4%. Generate 3-5 pillars and 30 angles mapped to unaware → aware → ready. Output as markdown table with pillar, stage, angle, hook seed, CTA direction."

## Invocation patterns

**Single-role:** user says "act as [role]" or names a deliverable that maps to one role.
- Load that role's reference file.
- Apply Operator Prompting formula. Ask for any missing Context inputs before generating.
- Return the role's standard deliverables.

**Full flow:** user says "run the marketing flow on X" or "use the 6-role team for X."
- Confirm all required Context inputs are available (audience source, offer details, prior content if any).
- Run roles in order 1 → 2 → 3 → 4. Stop after Role 4 unless user supplies performance data (then Role 5) or a proven asset (then Role 6).
- After each role, summarize deliverables and confirm before passing to the next.

**Operator Prompting only:** user wants to wrap an existing request in the formula without invoking the team. Return the rewritten prompt — do not execute it.

## Anti-patterns

- Do not invent audience pain points. Role 1 requires real source material (comments, reviews, transcripts). If absent, ask for it or stop.
- Do not skip Role 2 to jump from research to copy. Positioning shapes voice; copy without it is generic.
- Do not produce Role 6 variants by reformatting the same message. Golden Rule: same insight, different packaging — never the same message reused across formats.
- Do not run Role 5 without performance data. If user has none, route to Role 4 to ship first, then Role 5 after.

## Source

Framework by @shwetacreates / @shwetacreatesai (Instagram, "Let Him Cook" carousel). Captured in mindspace card `library/summit/build/2026-04-17-1144-claude-6-roles-marketing-team.md`.
