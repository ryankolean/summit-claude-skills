# Stage 3 — Cut script (EDL)

Claude reads `transcript.json` + `brief.md` and produces an Edit Decision List that picks the best takes, removes filler, orders clips, and inserts intentional pauses.

## Inputs
- `transcript.json` (stage 2)
- `brief.md` — one paragraph from user describing hook, audience, key points, target length, vibe.
- `manifest.json` (stage 1) for clip durations.

## Algorithm (Claude executes)

1. Parse brief → extract: target_seconds, hook_intent, key_points[], vibe, platform.
2. Walk transcript clip-by-clip. For each sentence boundary (use punctuation + > 0.4s gap heuristic):
   - Flag filler words for removal (see stage 2 list).
   - Score the sentence 0–10 against brief (information density, hook strength, redundancy w/ already-selected sentences).
3. Greedy pick highest-scoring sentences until cumulative duration approaches target_seconds.
4. Order to satisfy: hook within 0:00–0:03, payoff before midpoint, CTA in last 5s.
5. Insert micro-pauses (80ms) between cuts to avoid lip-pop.

## Output: `edl.json`

```json
{
  "target_duration": 60,
  "cuts": [
    {"clip": "clip-02", "in": 12.41, "out": 18.92, "label": "hook"},
    {"clip": "clip-01", "in": 3.10,  "out": 9.85,  "label": "context"},
    {"clip": "clip-01", "in": 22.40, "out": 31.15, "label": "key-point-1"},
    {"clip": "clip-03", "in": 4.20,  "out": 11.60, "label": "key-point-2"},
    {"clip": "clip-02", "in": 55.00, "out": 60.30, "label": "cta"}
  ],
  "removed_filler_count": 23,
  "estimated_duration": 58.7
}
```

## Quality gate
- Total duration within ±5% of target_seconds.
- No two adjacent cuts from the same clip with < 0.1s gap (looks like a glitch).
- Hook cut starts on a hard consonant if possible (clean audio in).

## Pitfalls
- Cutting mid-breath sounds awful. Snap cut points to nearest silence > 60ms.
- Aggressive filler removal can destroy rhythm. Keep one "uh" per 30s for naturalness.
- Don't cut on smile/laugh — visual continuity breaks.
