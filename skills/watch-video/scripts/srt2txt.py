#!/usr/bin/env python3
"""SRT -> '[MM:SS] text' lines. Collapses YouTube's rolling-duplicate cues."""
import re, sys

srt, offset = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0
TS = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->")

raw = open(srt, encoding="utf-8", errors="replace").read()
cues = []
for block in re.split(r"\n\s*\n", raw):
    lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
    idx = next((i for i, l in enumerate(lines) if TS.match(l)), None)
    if idx is None:
        continue
    h, mi, s, _ = map(int, TS.match(lines[idx]).groups())
    text = " ".join(re.sub(r"<[^>]+>", "", l) for l in lines[idx + 1:])
    if text.strip():
        cues.append((h * 3600 + mi * 60 + s + offset, " ".join(text.split())))

out, last = [], ""
for sec, cur in cues:
    if not cur or cur == last:
        continue
    if last and cur.startswith(last):          # cue repeats prior line, then extends it
        new, last = cur[len(last):].strip(), cur
        if new:
            out.append((sec, new))
    elif last and last.endswith(cur):          # cue is a tail we already emitted
        last = cur
    else:
        out.append((sec, cur))
        last = cur

for sec, text in out:
    print(f"[{sec // 60:02d}:{sec % 60:02d}] {text}")
