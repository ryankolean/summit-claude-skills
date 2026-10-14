"""Output directory, file naming, and JSON sidecars."""
import json
import re
from pathlib import Path


def slugify(text, max_len=40):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    slug = slug[:max_len].rstrip("-")
    return slug or "image"


def resolve_output_dir(brand, cwd):
    if brand is None:
        out = Path(cwd) / "generated"
    else:
        root = Path(brand.root).resolve()
        out = (root / brand.output_dir).resolve()
        if out != root and root not in out.parents:
            raise ValueError(f"brand output_dir {brand.output_dir!r} must stay inside {root}")
    out.mkdir(parents=True, exist_ok=True)
    return out


def output_path(out_dir, slug, genre, seed, suffix="", ext="png"):
    base = f"{slug}-{genre}-{seed}{suffix}"
    path = Path(out_dir) / f"{base}.{ext}"
    n = 2
    while path.exists():
        path = Path(out_dir) / f"{base}-{n}.{ext}"
        n += 1
    return path


def write_sidecar(image_path, record):
    side = Path(image_path).with_suffix(".json")
    side.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return side
