#!/usr/bin/env python3
"""Choose frame timestamps: scene cuts merged with uniform coverage.

usage: pick_times.py <start> <end> <cap> <mode> [scene_times_file]
"""
import sys

start, end, cap, mode = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
span = max(end - start, 0.0)
if span <= 0:
    sys.exit(0)

scenes = []
if len(sys.argv) > 5:
    try:
        scenes = [float(l) for l in open(sys.argv[5]) if l.strip()]
    except OSError:
        scenes = []
scenes = [t for t in scenes if start <= t <= end]

def uniform(n):
    n = max(int(n), 1)
    return [start + span * (i + 0.5) / n for i in range(n)]

if mode == "focused":
    times = uniform(min(span * 2, cap))
elif mode == "balanced" and len(scenes) >= 4:
    # cuts, plus enough uniform samples that long static stretches stay covered
    times = sorted(set(scenes) | set(uniform(min(span / 6, cap / 2))))
else:
    times = uniform(min(span / (1.5 if span <= 60 else 8), cap))
    if len(times) < 12:
        times = uniform(min(12, max(span, 1)))

# de-dupe within a second, then thin evenly to the cap
seen, kept = set(), []
for t in sorted(times):
    k = int(t)
    if k not in seen:
        seen.add(k)
        kept.append(k)
if len(kept) > cap:
    kept = [kept[round(i * (len(kept) - 1) / (cap - 1))] for i in range(cap)] if cap > 1 else kept[:1]

print("\n".join(str(t) for t in dict.fromkeys(kept)))
