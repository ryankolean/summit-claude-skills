# Role 2 — Brand Strategist

**Objective:** Decide what perception to own. Stand out or disappear.

## Required inputs (Context)

- Core offer (what you sell, who it's for, price point, format)
- Past content (3–5 representative posts, emails, or pages)
- Competitors in the same space (3–5 named, with links or content samples)
- Optional but preferred: Role 1 outputs (Pain-Desire Map + Language Bank)

If competitors or core offer are missing, stop and ask.

## Questions to answer

1. What category am I in? Name it precisely — and is there an adjacent category I could reframe into?
2. What makes me different on dimensions the audience actually cares about? (Cross-check against Role 1 desires.)
3. What perception should I own — one phrase, repeatable?
4. What's my strongest angle right now (where competitors are weakest + audience hunger is highest)?

## Deliverables

1. **3 Positioning Statements** — each in the form:
   > For [audience segment] who [pain or desire from Role 1], [offer] is the [category] that [unique mechanism], unlike [competitor pattern], because [proof].
2. **Niche Domination Angle** — one paragraph: the wedge issue where you can win for the next 12 months.
3. **Brand Voice Rules** — three lists:
   - Tone: 3–5 adjectives with example sentences.
   - Words to use: 10–20 (preferably from Role 1 Language Bank).
   - Words and phrases to avoid: 10–20 (industry clichés, competitor language, AI-slop tells).

## Operator Prompting prompt body

```
Role: Act as a senior brand strategist focused on category design and positioning.

Context: Core offer: [description, price, format]. Audience: [from Role 1 or stated]. Past content: [3–5 examples]. Competitors: [3–5 named with samples]. Optional: Role 1 Pain-Desire Map and Language Bank.

Objective: Lock in a positioning the audience will recognize and competitors cannot easily copy, and codify the voice rules so every future asset reinforces it.

Task: Define the precise category and one adjacent reframe option. Identify 3 differentiation dimensions the audience cares about. Draft 3 positioning statements using the format provided. Pick a 12-month domination angle. Codify Brand Voice Rules.

Output:
1. Positioning Statements — 3 variants in the For [X] who [Y]... format.
2. Niche Domination Angle — single paragraph + 1-line summary.
3. Brand Voice Rules — three markdown lists: Tone (with example sentences), Words to use, Words/phrases to avoid.
```

## Anti-patterns

- Do not generate positioning without competitor samples. Differentiation is relative.
- Do not let voice rules drift into generic ("authentic, bold, human"). Each adjective needs an example sentence.
- Avoid-list must include the exact slop words / clichés to suppress, not just categories.
