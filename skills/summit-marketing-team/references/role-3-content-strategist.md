# Role 3 — Content Strategist

**Objective:** Remove random posting. Every post serves a pillar and an awareness stage.

## Required inputs (Context)

- Brand positioning + Voice Rules (from Role 2)
- Pain-Desire Map + Language Bank (from Role 1)
- Core offer
- Historical content performance — top 3 and bottom 3 posts with metrics, if available

If Roles 1 and 2 outputs are missing, stop and ask. Strategy without positioning is guessing.

## Questions to answer

1. What 3–5 strategic content pillars cover the offer's full surface area?
2. For each pillar, what mix of authority + education vs. relatability + conversion angles?
3. How do angles map to the audience journey: unaware → aware → ready?
4. What weekly cadence balances all three stages without overweighting "ready" (selling) posts?

## Deliverables

1. **3–5 Content Pillars** — each named, defined in 1 sentence, with the audience promise.
2. **30 Strategic Ideas** — markdown table:
   | # | Pillar | Stage (unaware / aware / ready) | Angle (authority / education / relatability / conversion) | Hook seed | CTA direction |
3. **Structured Weekly Plan** — 7-day grid showing post type per day, balanced across pillars and stages. Specify platform if known.

## Operator Prompting prompt body

```
Role: Act as a senior content strategist who designs content systems, not one-off posts.

Context: Positioning + Voice Rules from Role 2. Pain-Desire Map + Language Bank from Role 1. Offer: [description]. Historical performance: [top 3 and bottom 3 posts with metrics, or "none yet"].

Objective: Replace ad-hoc posting with a pillar-based system that pulls audience from unaware to ready over 30 days.

Task: Define 3–5 content pillars. Generate 30 strategic ideas mapped to pillar, awareness stage, and angle type. Build a structured weekly plan that balances stages and pillars across 7 days.

Output:
1. Pillars — markdown list: name | 1-sentence definition | audience promise.
2. 30 Ideas — markdown table (#, pillar, stage, angle, hook seed, CTA direction).
3. Weekly Plan — 7-day markdown table (Day | Pillar | Stage | Angle | Format | Platform).
```

## Anti-patterns

- Do not generate ideas without referencing Role 1 pain points and Role 2 positioning. Each idea should be defensible against both.
- Do not let "ready" stage exceed 30% of the weekly plan. Selling posts dominate when upstream stages are starved.
- Hook seeds are seeds, not finished hooks. Role 4 finishes them.
