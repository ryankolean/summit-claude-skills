# invoke-image Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Claude skill that renders polished, brand-consistent website imagery through a local InvokeAI install at zero marginal cost.

**Architecture:** A Python CLI (`scripts/invoke.py`, run with `uv run --script`) backed by a small stdlib-only package (`scripts/invoke_image/`). Genre presets plus a per-client brand file produce prompts; captured InvokeAI node-graph templates are filled and posted to the local REST API; results are polled, downloaded, and written with a JSON sidecar. `SKILL.md` teaches Claude the brief, draft, review, final, upscale, vectorize loop.

**Tech Stack:** Python 3.11 to 3.13 via uv, stdlib `urllib` for HTTP, pytest, InvokeAI (native macOS Launcher install), ImageMagick 7 (`magick`, `montage`), vtracer (PyPI).

**Spec:** `docs/superpowers/specs/2026-10-14-invoke-image-design.md`

## Global Constraints

- Zero cost: no paid or hosted inference APIs, ever.
- Machine: Apple M1 Pro, 16GB unified memory. InvokeAI runs natively (Launcher install); no Docker for inference.
- InvokeAI API base: `http://127.0.0.1:9090`, single-user mode. Routers are mounted under `/api` (`/api/v1/...`, `/api/v2/models/...`).
- Package `scripts/invoke_image/` uses the Python standard library only. The only third-party runtime dependency is `vtracer`, declared inline in `scripts/invoke.py` (`requires-python = ">=3.11,<3.14"`).
- Test command (run from `skills/invoke-image/`): `uv run --python 3.13 --with pytest --with vtracer pytest tests -q`
- Brand file: `<client-repo>/.claude/image-brand.json`. A brand file may not set `model`, `models`, `loras`, `license`, or `allowed_models`.
- License gate: when a brand file is present, every model, LoRA, and the upscaler must have `commercial_ok: true`. A missing `commercial_ok` counts as false.
- Output naming: `<output_dir>/<slug>-<genre>-<seed>.png` plus a same-name `.json` sidecar. Drafts add `-draft` before the extension.
- Speed gate: any model slower than 300 seconds per 1024x1024 image is removed from genre defaults.
- No silent fallbacks: never substitute a model; surface InvokeAI error text verbatim.
- Repo is public: no client data, brand files, or generated client images in summit-claude-skills.
- No emojis and no em dashes in any file, commit, or PR text. Conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Commit messages: write the message with the Write tool to a scratch file and use `git commit -F <file>` (inline `-m` mangles `$` amounts and newlines in this environment). Never `--no-verify`, never `--no-gpg-sign`.
- Delivery: all work lands via pull requests. Nothing is merged without explicit user approval.
- Branches: this plan is committed on `docs/invoke-image-spec` (PR #10). Implementation goes on `feat/invoke-image`, branched from `docs/invoke-image-spec`, in the worktree `~/summit-claude-skills-invoke-image`. Never touch the main checkout `~/summit-claude-skills` (a parallel session owns it).

## Spec Deviations (decided while planning; confirm at plan review)

1. **Draft pass uses reduced steps on the same model, not FLUX.1-schnell.** A seed only reproduces a composition on the same model, so drafting on schnell would break "re-render the chosen seed on the final model". `draft_steps(n)` = `n` if `n <= 8`, else `max(8, round(n * 0.4))`.
2. **`invoke.py` is a thin CLI over a small package** (`scripts/invoke_image/`) instead of one file, so each unit is testable without a server.
3. **OOM retry lowers resolution only** (0.75x, rounded to the family multiple). It does not switch quantization, because that would be a model substitution.
4. **Seamless textures use a captured `sdxl-seamless` template variant**, selected by a genre's `template_suffix`.
5. **Run timeout counts from when the job starts running**, not from enqueue, so a job waiting behind your own UI work is not killed. A job still pending after 1800s is canceled with a "queue paused?" error.
6. **LoRA support (Task 14) runs only if Fly Trap acceptance needs it.** Until then a genre with LoRAs fails loudly because its `-lora` template does not exist.

## Review Focus

1. Brand file above the repo (for example a stray `~/.claude/image-brand.json`): the search stops at the first directory containing `.git`, so a file outside the client repo is never applied. Pinned in Task 2 (`test_find_brand_stops_at_git_root`).
2. Brand `output_dir` escaping the repo (`../x`, absolute paths): rejected before any file is written. Pinned in Task 3 (`test_output_dir_must_stay_in_repo`).
3. Subjects containing braces (`{brand}`, `{{seed}}`): treated as literal text, never re-expanded, never crash. Pinned in Task 2 (`test_merge_keeps_braces_in_subject_literal`) and Task 4 (`test_fill_does_not_reexpand_braces_in_values`).
4. A model entry missing `commercial_ok`: fails closed for client work. Pinned in Task 2 (`test_license_gate_missing_flag_fails_closed`).
5. Job queued behind your own InvokeAI UI renders: pending time does not count toward the run timeout; a stalled queue still ends with a clear error. Pinned in Task 5 (`test_wait_timeout_counts_running_time_and_cancels`, `test_wait_stalled_queue_canceled`).

## File Structure

```
skills/invoke-image/
  SKILL.md                     Claude-facing instructions (Task 13)
  models.json                  model registry, pinned InvokeAI version, server start command (Task 7)
  genres/*.json                8 starter genre presets (Task 10)
  graphs/                      captured node-graph templates: sdxl, sdxl-seamless, flux, upscale (Task 8)
  graphs/raw/                  raw captured enqueue_batch bodies, kept for recapture diffs (Task 8)
  scripts/invoke.py            CLI entry: argparse, subcommands, exit codes
  scripts/invoke_image/
    __init__.py
    sizing.py                  aspect ratio -> pixel dimensions per family
    styles.py                  Genre, Brand, Prompt; load, merge, model resolution, license gate
    output.py                  slug, output dir, file naming, sidecar
    graph.py                   template load/fill, capture helpers, result parsing
    client.py                  InvokeAI REST client (transport injectable)
    runner.py                  render jobs: fill, enqueue, wait, OOM retry, download, sidecar
    vector.py                  posterize, trace to SVG, rasterize for inspection
  tests/
    conftest.py
    fixtures/skill/            fake models.json, genre, graph for CLI tests
    test_*.py
```

Exit codes for `invoke.py`: 0 ok, 2 config or input error, 3 InvokeAI version mismatch, 4 server or queue error.

---

### Task 0: Branch and commit this plan

**Files:**
- Create: `docs/superpowers/plans/2026-10-14-invoke-image.md` (this file)

- [ ] **Step 1: Commit the plan on the spec branch and push**

```bash
cd ~/summit-claude-skills-invoke-image
git branch --show-current   # expect: docs/invoke-image-spec
git add docs/superpowers/plans/2026-10-14-invoke-image.md
git commit -F <scratch>/msg.txt   # message: "docs: add invoke-image implementation plan"
git push
```

- [ ] **Step 2: Create the implementation branch**

```bash
git switch -c feat/invoke-image
mkdir -p skills/invoke-image/scripts/invoke_image skills/invoke-image/tests
```

---

### Task 1: Scaffold and sizing

**Files:**
- Create: `skills/invoke-image/scripts/invoke_image/__init__.py`
- Create: `skills/invoke-image/scripts/invoke_image/sizing.py`
- Create: `skills/invoke-image/tests/conftest.py`
- Test: `skills/invoke-image/tests/test_sizing.py`

**Interfaces:**
- Produces: `sizing.ASPECTS: dict[str, float]`, `sizing.MULTIPLE: dict[str, int]`, `sizing.dimensions(aspect: str, family: str, area: int = 1048576) -> tuple[int, int]`, `sizing.scaled(width: int, height: int, factor: float, family: str) -> tuple[int, int]`. Raises `ValueError` for unknown aspect or family.

- [ ] **Step 1: Write conftest and the failing test**

`tests/conftest.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
```

`tests/test_sizing.py`:

```python
import pytest

from invoke_image import sizing


@pytest.mark.parametrize(
    "aspect,family,expected",
    [
        ("1:1", "sdxl", (1024, 1024)),
        ("4:3", "sdxl", (1152, 896)),
        ("3:4", "sdxl", (896, 1152)),
        ("16:9", "sdxl", (1344, 768)),
        ("9:16", "sdxl", (768, 1344)),
        ("3:2", "sdxl", (1280, 832)),
        ("2:3", "sdxl", (832, 1280)),
        ("21:9", "sdxl", (1536, 640)),
        ("1:1", "flux", (1024, 1024)),
        ("4:3", "flux", (1184, 880)),
        ("16:9", "flux", (1360, 768)),
        ("9:16", "flux", (768, 1360)),
        ("3:2", "flux", (1248, 832)),
        ("21:9", "flux", (1568, 672)),
    ],
)
def test_dimensions(aspect, family, expected):
    assert sizing.dimensions(aspect, family) == expected


def test_dimensions_respect_family_multiple():
    for aspect in sizing.ASPECTS:
        w, h = sizing.dimensions(aspect, "sdxl")
        assert w % 64 == 0 and h % 64 == 0
        w, h = sizing.dimensions(aspect, "flux")
        assert w % 16 == 0 and h % 16 == 0


def test_small_area_for_selftest():
    assert sizing.dimensions("1:1", "sdxl", area=512 * 512) == (512, 512)


def test_unknown_aspect_lists_options():
    with pytest.raises(ValueError, match="16:9"):
        sizing.dimensions("5:4", "sdxl")


def test_unknown_family():
    with pytest.raises(ValueError, match="family"):
        sizing.dimensions("1:1", "sd15")


def test_scaled_for_oom_retry():
    assert sizing.scaled(1344, 768, 0.75, "sdxl") == (1024, 576)
    assert sizing.scaled(1360, 768, 0.75, "flux") == (1024, 576)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_sizing.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'invoke_image'`

- [ ] **Step 3: Write minimal implementation**

`scripts/invoke_image/__init__.py`:

```python
"""invoke-image: drive a local InvokeAI to render brand-consistent images."""
```

`scripts/invoke_image/sizing.py`:

```python
"""Aspect ratio to pixel dimensions for each model family."""
import math

ASPECTS = {
    "1:1": 1.0,
    "4:3": 4 / 3,
    "3:4": 3 / 4,
    "16:9": 16 / 9,
    "9:16": 9 / 16,
    "3:2": 3 / 2,
    "2:3": 2 / 3,
    "21:9": 21 / 9,
}
MULTIPLE = {"sdxl": 64, "flux": 16}
DEFAULT_AREA = 1024 * 1024


def _round(value, multiple):
    return max(multiple, round(value / multiple) * multiple)


def _multiple(family):
    if family not in MULTIPLE:
        raise ValueError(f"unknown model family {family!r}; expected one of {', '.join(MULTIPLE)}")
    return MULTIPLE[family]


def dimensions(aspect, family, area=DEFAULT_AREA):
    if aspect not in ASPECTS:
        raise ValueError(f"unknown aspect {aspect!r}; use one of {', '.join(ASPECTS)}")
    multiple = _multiple(family)
    ratio = ASPECTS[aspect]
    width = math.sqrt(area * ratio)
    return _round(width, multiple), _round(width / ratio, multiple)


def scaled(width, height, factor, family):
    multiple = _multiple(family)
    return _round(width * factor, multiple), _round(height * factor, multiple)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_sizing.py -q`
Expected: PASS (19 passed)

- [ ] **Step 5: Commit**

```bash
git add skills/invoke-image/scripts skills/invoke-image/tests
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add aspect sizing"
```

---

### Task 2: Genres, brand overlay, prompt merge, license gate

**Files:**
- Create: `skills/invoke-image/scripts/invoke_image/styles.py`
- Test: `skills/invoke-image/tests/test_styles.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `StyleError(Exception)`
  - `Genre` dataclass: `name: str, model: str, allowed_models: list, positive: str, negative: str, steps: int, cfg: float, loras: list = [], vectorize: bool = False, template_suffix: str = ""`
  - `Brand` dataclass: `client: str, brand: str, root: Path, avoid: list = [], default_genres: list = [], output_dir: str = "generated"`
  - `Prompt` dataclass: `positive: str, negative: str`
  - `load_genre(genres_dir: Path, name: str) -> Genre`
  - `load_brand(path: Path) -> Brand`
  - `find_brand(start: Path) -> Brand | None`
  - `merge(genre: Genre, subject: str, brand: Brand | None = None) -> Prompt`
  - `resolve_model(genre: Genre, registry: dict, override: str | None = None) -> tuple[str, dict]`
  - `resolve_loras(genre: Genre, registry: dict) -> list[tuple[str, dict, float]]`
  - `check_license(entries: list[tuple[str, dict]], brand: Brand | None) -> None`
  - `preset_positive(genre: Genre) -> str`

- [ ] **Step 1: Write the failing test**

`tests/test_styles.py`:

```python
import json

import pytest

from invoke_image import styles

GENRE = {
    "name": "photo",
    "model": "m-ok",
    "allowed_models": ["m-ok", "m-nc"],
    "positive": "{subject}, photograph, {brand}",
    "negative": "blurry, watermark",
    "steps": 30,
    "cfg": 5.0,
}
REGISTRY = {
    "models": {
        "m-ok": {"invoke_key": "k1", "license": "openrail++", "commercial_ok": True},
        "m-nc": {"invoke_key": "k2", "license": "cc-by-nc-4.0", "commercial_ok": False},
        "m-unknown": {"invoke_key": "k3", "license": "unclear"},
    },
    "loras": {"l-ok": {"invoke_key": "k4", "license": "mit", "commercial_ok": True}},
}


def write_genre(tmp_path, **overrides):
    data = {**GENRE, **overrides}
    genres = tmp_path / "genres"
    genres.mkdir(exist_ok=True)
    (genres / f"{data['name']}.json").write_text(json.dumps(data))
    return genres


def write_brand(root, **fields):
    data = {"client": "Fly Trap", "brand": "warm cream, diner red", "avoid": ["readable text"], **fields}
    (root / ".claude").mkdir(parents=True, exist_ok=True)
    (root / ".claude" / "image-brand.json").write_text(json.dumps(data))
    return root


def brand_at(root, **fields):
    return styles.load_brand(write_brand(root, **fields) / ".claude" / "image-brand.json")


def test_load_genre(tmp_path):
    g = styles.load_genre(write_genre(tmp_path), "photo")
    assert g.model == "m-ok" and g.steps == 30
    assert g.loras == [] and g.vectorize is False and g.template_suffix == ""


def test_unknown_genre_lists_available(tmp_path):
    with pytest.raises(styles.StyleError, match="available: photo"):
        styles.load_genre(write_genre(tmp_path), "nope")


def test_genre_without_subject_slot_rejected(tmp_path):
    with pytest.raises(styles.StyleError, match="subject"):
        styles.load_genre(write_genre(tmp_path, positive="photograph"), "photo")


def test_genre_default_model_must_be_allowed(tmp_path):
    with pytest.raises(styles.StyleError, match="allowed_models"):
        styles.load_genre(write_genre(tmp_path, model="m-x"), "photo")


def test_genre_unknown_key_rejected(tmp_path):
    with pytest.raises(styles.StyleError, match="colour"):
        styles.load_genre(write_genre(tmp_path, colour="red"), "photo")


def test_merge_without_brand(tmp_path):
    g = styles.load_genre(write_genre(tmp_path), "photo")
    p = styles.merge(g, "  pancakes on a diner counter ")
    assert p.positive == "pancakes on a diner counter, photograph"
    assert p.negative == "blurry, watermark"


def test_merge_with_brand(tmp_path):
    g = styles.load_genre(write_genre(tmp_path), "photo")
    p = styles.merge(g, "pancakes", brand_at(tmp_path / "site"))
    assert p.positive == "pancakes, photograph, warm cream, diner red"
    assert p.negative == "blurry, watermark, readable text"


def test_merge_keeps_braces_in_subject_literal(tmp_path):
    g = styles.load_genre(write_genre(tmp_path), "photo")
    assert styles.merge(g, "sign reading {brand}").positive == "sign reading {brand}, photograph"


def test_merge_empty_subject_rejected(tmp_path):
    g = styles.load_genre(write_genre(tmp_path), "photo")
    with pytest.raises(styles.StyleError, match="subject"):
        styles.merge(g, "   ")


def test_find_brand_walks_up(tmp_path):
    site = write_brand(tmp_path / "site")
    (site / ".git").mkdir()
    deep = site / "a" / "b"
    deep.mkdir(parents=True)
    brand = styles.find_brand(deep)
    assert brand.client == "Fly Trap" and brand.root == site.resolve()


def test_find_brand_stops_at_git_root(tmp_path):
    write_brand(tmp_path)
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    assert styles.find_brand(repo) is None


def test_find_brand_none(tmp_path):
    (tmp_path / ".git").mkdir()
    assert styles.find_brand(tmp_path) is None


@pytest.mark.parametrize("key", ["model", "models", "loras", "license", "allowed_models"])
def test_brand_cannot_set_model_or_license(tmp_path, key):
    path = write_brand(tmp_path, **{key: "x"}) / ".claude" / "image-brand.json"
    with pytest.raises(styles.StyleError, match=f"may not set {key}"):
        styles.load_brand(path)


def test_brand_requires_client_and_brand(tmp_path):
    path = write_brand(tmp_path, brand="") / ".claude" / "image-brand.json"
    with pytest.raises(styles.StyleError, match="required field 'brand'"):
        styles.load_brand(path)


def test_resolve_model_default_and_override(tmp_path):
    g = styles.load_genre(write_genre(tmp_path), "photo")
    assert styles.resolve_model(g, REGISTRY)[0] == "m-ok"
    assert styles.resolve_model(g, REGISTRY, "m-nc") == ("m-nc", REGISTRY["models"]["m-nc"])


def test_resolve_model_rejects_disallowed(tmp_path):
    g = styles.load_genre(write_genre(tmp_path), "photo")
    with pytest.raises(styles.StyleError, match="not allowed"):
        styles.resolve_model(g, REGISTRY, "m-unknown")


def test_resolve_model_missing_from_registry(tmp_path):
    g = styles.load_genre(write_genre(tmp_path, allowed_models=["m-ok", "ghost"]), "photo")
    with pytest.raises(styles.StyleError, match="models.json"):
        styles.resolve_model(g, REGISTRY, "ghost")


def test_resolve_loras(tmp_path):
    g = styles.load_genre(write_genre(tmp_path, loras=[{"key": "l-ok", "weight": 0.7}]), "photo")
    assert styles.resolve_loras(g, REGISTRY) == [("l-ok", REGISTRY["loras"]["l-ok"], 0.7)]
    g2 = styles.load_genre(write_genre(tmp_path, loras=[{"key": "ghost"}]), "photo")
    with pytest.raises(styles.StyleError, match="ghost"):
        styles.resolve_loras(g2, REGISTRY)


def test_license_gate_blocks_noncommercial_for_brand(tmp_path):
    with pytest.raises(styles.StyleError, match="cc-by-nc-4.0"):
        styles.check_license([("m-nc", REGISTRY["models"]["m-nc"])], brand_at(tmp_path))


def test_license_gate_missing_flag_fails_closed(tmp_path):
    with pytest.raises(styles.StyleError, match="m-unknown"):
        styles.check_license([("m-unknown", REGISTRY["models"]["m-unknown"])], brand_at(tmp_path))


def test_license_gate_allows_noncommercial_without_brand():
    styles.check_license([("m-nc", REGISTRY["models"]["m-nc"])], None)


def test_preset_positive(tmp_path):
    g = styles.load_genre(write_genre(tmp_path), "photo")
    assert styles.preset_positive(g) == "{prompt}, photograph"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_styles.py -q`
Expected: FAIL with `ImportError: cannot import name 'styles'`

- [ ] **Step 3: Write minimal implementation**

`scripts/invoke_image/styles.py`:

```python
"""Genre presets, per-client brand overlay, prompt merge, license gate."""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

BRAND_FILE = Path(".claude") / "image-brand.json"
BRAND_FORBIDDEN = ("model", "models", "loras", "license", "allowed_models")
SLOT = re.compile(r"\{(subject|brand)\}")


class StyleError(Exception):
    pass


@dataclass
class Genre:
    name: str
    model: str
    allowed_models: list
    positive: str
    negative: str
    steps: int
    cfg: float
    loras: list = field(default_factory=list)
    vectorize: bool = False
    template_suffix: str = ""


@dataclass
class Brand:
    client: str
    brand: str
    root: Path
    avoid: list = field(default_factory=list)
    default_genres: list = field(default_factory=list)
    output_dir: str = "generated"


@dataclass
class Prompt:
    positive: str
    negative: str


def _clean(text):
    return ", ".join(part.strip() for part in text.split(",") if part.strip())


def load_genre(genres_dir, name):
    path = Path(genres_dir) / f"{name}.json"
    if not path.is_file():
        known = sorted(p.stem for p in Path(genres_dir).glob("*.json"))
        raise StyleError(f"unknown genre {name!r}; available: {', '.join(known)}")
    data = json.loads(path.read_text())
    try:
        genre = Genre(**data)
    except TypeError as exc:
        raise StyleError(f"{path}: {exc}") from exc
    if "{subject}" not in genre.positive:
        raise StyleError(f"{path}: positive template has no {{subject}} slot")
    if genre.model not in genre.allowed_models:
        raise StyleError(f"{path}: default model {genre.model!r} is not in allowed_models")
    return genre


def load_brand(path):
    path = Path(path)
    data = json.loads(path.read_text())
    blocked = [key for key in BRAND_FORBIDDEN if key in data]
    if blocked:
        raise StyleError(
            f"{path}: brand files may not set {', '.join(blocked)}; "
            "model and license come from the genre and models.json"
        )
    for key in ("client", "brand"):
        if not data.get(key):
            raise StyleError(f"{path}: missing required field {key!r}")
    try:
        return Brand(root=path.resolve().parent.parent, **data)
    except TypeError as exc:
        raise StyleError(f"{path}: {exc}") from exc


def find_brand(start):
    start = Path(start).resolve()
    for directory in [start, *start.parents]:
        candidate = directory / BRAND_FILE
        if candidate.is_file():
            return load_brand(candidate)
        if (directory / ".git").exists():
            return None
    return None


def merge(genre, subject, brand=None):
    subject = subject.strip()
    if not subject:
        raise StyleError("subject is empty")
    slots = {"subject": subject, "brand": brand.brand if brand else ""}
    positive = SLOT.sub(lambda m: slots[m.group(1)], genre.positive)
    negative = ", ".join([genre.negative, *(brand.avoid if brand else [])])
    return Prompt(_clean(positive), _clean(negative))


def resolve_model(genre, registry, override=None):
    name = override or genre.model
    if name not in genre.allowed_models:
        raise StyleError(
            f"model {name!r} is not allowed for genre {genre.name!r}; "
            f"allowed: {', '.join(genre.allowed_models)}"
        )
    entry = registry["models"].get(name)
    if entry is None:
        raise StyleError(f"model {name!r} is missing from models.json")
    return name, entry


def resolve_loras(genre, registry):
    resolved = []
    for item in genre.loras:
        entry = registry.get("loras", {}).get(item["key"])
        if entry is None:
            raise StyleError(f"LoRA {item['key']!r} used by genre {genre.name!r} is missing from models.json")
        resolved.append((item["key"], entry, float(item.get("weight", 1.0))))
    return resolved


def check_license(entries, brand):
    if brand is None:
        return
    for name, entry in entries:
        if entry.get("commercial_ok") is not True:
            raise StyleError(
                f"{name} is licensed {entry.get('license', 'unknown')!r} and is not marked "
                f"commercial_ok; refusing client output for {brand.client}"
            )


def preset_positive(genre):
    return _clean(genre.positive.replace("{subject}", "{prompt}").replace("{brand}", ""))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_styles.py -q`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add skills/invoke-image/scripts/invoke_image/styles.py skills/invoke-image/tests/test_styles.py
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add genre and brand style system"
```

---

### Task 3: Output naming, output directory, sidecar

**Files:**
- Create: `skills/invoke-image/scripts/invoke_image/output.py`
- Test: `skills/invoke-image/tests/test_output.py`

**Interfaces:**
- Consumes: `styles.Brand` (Task 2).
- Produces:
  - `slugify(text: str, max_len: int = 40) -> str`
  - `resolve_output_dir(brand: Brand | None, cwd: Path) -> Path` (creates the dir; `ValueError` if outside brand root)
  - `output_path(out_dir: Path, slug: str, genre: str, seed: int | str, suffix: str = "", ext: str = "png") -> Path` (never returns an existing path)
  - `write_sidecar(image_path: Path, record: dict) -> Path`

- [ ] **Step 1: Write the failing test**

`tests/test_output.py`:

```python
import json

import pytest

from invoke_image import output, styles


def test_slugify():
    assert output.slugify("Pancakes on a Diner Counter, 7am!") == "pancakes-on-a-diner-counter-7am"
    assert output.slugify("!!!") == "image"
    long = output.slugify("word " * 30)
    assert len(long) <= 40 and not long.endswith("-")


def test_output_path_and_collision(tmp_path):
    first = output.output_path(tmp_path, "pancakes", "photographic", 42)
    assert first.name == "pancakes-photographic-42.png"
    first.write_bytes(b"x")
    second = output.output_path(tmp_path, "pancakes", "photographic", 42)
    assert second.name == "pancakes-photographic-42-2.png"


def test_output_path_draft_suffix(tmp_path):
    assert output.output_path(tmp_path, "a", "g", 1, suffix="-draft").name == "a-g-1-draft.png"


def test_sidecar(tmp_path):
    png = tmp_path / "a-g-1.png"
    png.write_bytes(b"x")
    side = output.write_sidecar(png, {"seed": 1, "model": "m"})
    assert side.name == "a-g-1.json"
    assert json.loads(side.read_text()) == {"model": "m", "seed": 1}


def test_output_dir_without_brand(tmp_path):
    out = output.resolve_output_dir(None, tmp_path)
    assert out == tmp_path / "generated" and out.is_dir()


def test_output_dir_with_brand(tmp_path):
    brand = styles.Brand(client="c", brand="b", root=tmp_path, output_dir="assets/generated")
    out = output.resolve_output_dir(brand, tmp_path / "elsewhere")
    assert out == (tmp_path / "assets" / "generated").resolve() and out.is_dir()


@pytest.mark.parametrize("bad", ["../outside", "/tmp/abs", "assets/../../x"])
def test_output_dir_must_stay_in_repo(tmp_path, bad):
    brand = styles.Brand(client="c", brand="b", root=tmp_path, output_dir=bad)
    with pytest.raises(ValueError, match="inside"):
        output.resolve_output_dir(brand, tmp_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_output.py -q`
Expected: FAIL with `ImportError: cannot import name 'output'`

- [ ] **Step 3: Write minimal implementation**

`scripts/invoke_image/output.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_output.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/invoke-image/scripts/invoke_image/output.py skills/invoke-image/tests/test_output.py
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add output naming and sidecars"
```

---

### Task 4: Graph templates: fill, capture helpers, result parsing

**Files:**
- Create: `skills/invoke-image/scripts/invoke_image/graph.py`
- Test: `skills/invoke-image/tests/test_graph.py`

**Interfaces:**
- Produces:
  - `GraphError(Exception)`
  - `load_template(graphs_dir: Path, name: str) -> dict` (GraphError "not captured yet" if missing)
  - `placeholders(node) -> set[str]`
  - `fill(template: dict, values: dict) -> dict` (deep copy; exact `"{{k}}"` strings take the value with its type; embedded ones are stringified; single pass, no re-expansion; GraphError on missing values)
  - `collapse_batch_data(batch: dict) -> dict` (applies `batch["data"]` first items onto `batch["graph"]` nodes)
  - `templatize(graph: dict, sentinels: dict) -> tuple[dict, dict[str, int]]`
  - `output_image_names(queue_item: dict) -> list[str]`

- [ ] **Step 1: Write the failing test**

`tests/test_graph.py`:

```python
import pytest

from invoke_image import graph

TEMPLATE = {
    "id": "g",
    "nodes": {
        "pos": {"prompt": "{{positive}}"},
        "meta": {"note": "made with {{positive}} at {{seed}}"},
        "noise": {"seed": "{{seed}}", "width": "{{width}}"},
        "model": {"model": "{{model}}"},
    },
    "edges": [],
}


def test_placeholders():
    assert graph.placeholders(TEMPLATE) == {"positive", "seed", "width", "model"}


def test_fill_types():
    out = graph.fill(TEMPLATE, {"positive": "pancakes", "seed": 7, "width": 1024, "model": {"key": "k"}})
    assert out["nodes"]["noise"] == {"seed": 7, "width": 1024}
    assert out["nodes"]["model"]["model"] == {"key": "k"}
    assert out["nodes"]["meta"]["note"] == "made with pancakes at 7"
    assert TEMPLATE["nodes"]["noise"]["seed"] == "{{seed}}"


def test_fill_missing_value():
    with pytest.raises(graph.GraphError, match="model"):
        graph.fill(TEMPLATE, {"positive": "p", "seed": 1, "width": 1})


def test_fill_extra_values_ignored():
    assert graph.fill({"a": "{{seed}}"}, {"seed": 1, "negative": "unused"}) == {"a": 1}


def test_fill_does_not_reexpand_braces_in_values():
    out = graph.fill({"p": "{{positive}}", "q": "x {{positive}}"}, {"positive": "sign that says {{seed}}"})
    assert out == {"p": "sign that says {{seed}}", "q": "x sign that says {{seed}}"}


def test_load_template_missing(tmp_path):
    with pytest.raises(graph.GraphError, match="not captured"):
        graph.load_template(tmp_path, "sdxl")


def test_collapse_batch_data():
    batch = {
        "graph": {"nodes": {"noise": {"seed": 0}, "pos": {"prompt": ""}}},
        "data": [
            [{"node_path": "noise", "field_name": "seed", "items": [424242, 5]}],
            [{"node_path": "pos", "field_name": "prompt", "items": ["XPOSX"]}],
        ],
    }
    g = graph.collapse_batch_data(batch)
    assert g["nodes"]["noise"]["seed"] == 424242
    assert g["nodes"]["pos"]["prompt"] == "XPOSX"
    assert batch["graph"]["nodes"]["noise"]["seed"] == 0


def test_templatize():
    raw = {
        "nodes": {
            "pos": {"prompt": "XPOSX"},
            "neg": {"prompt": "XNEGX"},
            "meta": {
                "positive_prompt": "XPOSX",
                "model": {"key": "mk", "name": "Jugg"},
                "seed": 424242,
                "steps": 23,
                "cfg_scale": 5.5,
                "use_cache": True,
            },
            "noise": {"seed": 424242, "width": 1152, "height": 896},
            "out": {"board": {"board_id": "bid"}, "is_intermediate": False},
        }
    }
    sentinels = {
        "positive": "XPOSX",
        "negative": "XNEGX",
        "seed": 424242,
        "width": 1152,
        "height": 896,
        "steps": 23,
        "cfg": 5.5,
        "model": {"key": "mk"},
        "board": {"board_id": "bid"},
    }
    t, counts = graph.templatize(raw, sentinels)
    assert counts == {
        "positive": 2, "negative": 1, "seed": 2, "width": 1, "height": 1,
        "steps": 1, "cfg": 1, "model": 1, "board": 1,
    }
    assert t["nodes"]["meta"]["model"] == "{{model}}"
    assert t["nodes"]["meta"]["use_cache"] is True
    assert t["nodes"]["out"]["is_intermediate"] is False
    assert graph.placeholders(t) == set(sentinels)


def test_templatize_int_sentinel_does_not_match_bool():
    t, counts = graph.templatize({"a": True, "b": 1}, {"steps": 1})
    assert t == {"a": True, "b": "{{steps}}"} and counts == {"steps": 1}


def test_output_image_names():
    item = {
        "session": {
            "results": {
                "x": {"type": "latents_output"},
                "y": {"type": "image_output", "image": {"image_name": "a.png"}},
                "z": {"type": "image_output", "image": {"image_name": "b.png"}},
                "w": {"type": "image_output", "image": {"image_name": "a.png"}},
            }
        }
    }
    assert graph.output_image_names(item) == ["a.png", "b.png"]
    assert graph.output_image_names({"session": {}}) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_graph.py -q`
Expected: FAIL with `ImportError: cannot import name 'graph'`

- [ ] **Step 3: Write minimal implementation**

`scripts/invoke_image/graph.py`:

```python
"""InvokeAI node-graph templates: load, fill, capture helpers, result parsing."""
import copy
import json
import re
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


class GraphError(Exception):
    pass


def load_template(graphs_dir, name):
    path = Path(graphs_dir) / f"{name}.json"
    if not path.is_file():
        raise GraphError(f"graph template {name!r} not captured yet ({path}); see SKILL.md 'Recapturing templates'")
    return json.loads(path.read_text())


def placeholders(node):
    found = set()
    if isinstance(node, dict):
        for value in node.values():
            found |= placeholders(value)
    elif isinstance(node, list):
        for value in node:
            found |= placeholders(value)
    elif isinstance(node, str):
        found |= set(PLACEHOLDER.findall(node))
    return found


def fill(template, values):
    missing = placeholders(template) - set(values)
    if missing:
        raise GraphError(f"no value for placeholders: {', '.join(sorted(missing))}")
    return _fill(template, values)


def _fill(node, values):
    if isinstance(node, dict):
        return {key: _fill(value, values) for key, value in node.items()}
    if isinstance(node, list):
        return [_fill(value, values) for value in node]
    if isinstance(node, str):
        whole = PLACEHOLDER.fullmatch(node)
        if whole:
            return copy.deepcopy(values[whole.group(1)])
        return PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), node)
    return node


def collapse_batch_data(batch):
    result = copy.deepcopy(batch["graph"])
    for group in batch.get("data") or []:
        for datum in group:
            if datum["items"]:
                result["nodes"][datum["node_path"]][datum["field_name"]] = datum["items"][0]
    return result


def templatize(node, sentinels):
    counts = {name: 0 for name in sentinels}

    def walk(n):
        if isinstance(n, dict):
            for name, sentinel in sentinels.items():
                if isinstance(sentinel, dict) and all(n.get(k) == v for k, v in sentinel.items()):
                    counts[name] += 1
                    return "{{" + name + "}}"
            return {key: walk(value) for key, value in n.items()}
        if isinstance(n, list):
            return [walk(value) for value in n]
        if isinstance(n, str):
            for name, sentinel in sentinels.items():
                if isinstance(sentinel, str) and sentinel in n:
                    counts[name] += 1
                    n = n.replace(sentinel, "{{" + name + "}}")
            return n
        for name, sentinel in sentinels.items():
            if not isinstance(sentinel, (dict, str)) and type(n) is type(sentinel) and n == sentinel:
                counts[name] += 1
                return "{{" + name + "}}"
        return n

    return walk(copy.deepcopy(node)), counts


def output_image_names(queue_item):
    results = (queue_item.get("session") or {}).get("results") or {}
    names = []
    for out in results.values():
        if isinstance(out, dict) and out.get("type") == "image_output":
            name = (out.get("image") or {}).get("image_name")
            if name and name not in names:
                names.append(name)
    return names
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_graph.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/invoke-image/scripts/invoke_image/graph.py skills/invoke-image/tests/test_graph.py
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add graph template fill and capture helpers"
```

---

### Task 5: InvokeAI REST client

**Files:**
- Create: `skills/invoke-image/scripts/invoke_image/client.py`
- Test: `skills/invoke-image/tests/test_client.py`

**Interfaces:**
- Produces:
  - `InvokeError(Exception)`; `HTTPStatusError(InvokeError)` with `.status`; `QueueItemFailed(InvokeError)` with `.item`
  - `urllib_transport(method, url, body=None, headers=None) -> (status: int, data: bytes)`; raises `OSError` on connection failure
  - `spawn_server(cmd: list[str], log_path: Path) -> None`
  - `Client(base="http://127.0.0.1:9090", transport=urllib_transport, sleep=time.sleep, clock=time.monotonic)` with attribute `.transport` and methods:
    - `request(method, path, payload=None, query=None, raw_body=None, headers=None) -> bytes`
    - `call(...) -> object | None` (JSON-decoded `request`)
    - `version() -> str | None`
    - `ensure_running(start_cmd: list[str], log_path: Path, timeout=120, spawn=None) -> str`
    - `model(key: str) -> dict` (`key, hash, name, base, type`)
    - `board_id(name: str) -> str`
    - `board_image_names(board_id: str) -> list[str]`
    - `enqueue(graph: dict) -> list[int]`
    - `wait(item_id: int, timeout: float, poll=2.0, pending_limit=1800) -> dict`
    - `image_dto(name: str) -> dict`
    - `download(name: str, dest: Path) -> Path`
    - `list_presets() -> list[dict]`, `create_preset(name, positive, negative) -> dict`, `update_preset(preset_id, name, positive, negative) -> dict`

- [ ] **Step 1: Write the failing test**

`tests/test_client.py`:

```python
import json

import pytest

from invoke_image.client import Client, InvokeError, QueueItemFailed


class Script:
    def __init__(self, steps):
        self.steps, self.calls = list(steps), []

    def __call__(self, method, url, body=None, headers=None):
        self.calls.append((method, url, body, headers))
        assert self.steps, f"unexpected call {method} {url}"
        exp_method, exp_path, status, payload = self.steps.pop(0)
        assert method == exp_method and exp_path in url, (method, url, exp_method, exp_path)
        if isinstance(payload, BaseException):
            raise payload
        return status, payload if isinstance(payload, bytes) else json.dumps(payload).encode()


class Clock:
    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds


def make(steps):
    clock = Clock()
    return Client(transport=Script(steps), sleep=clock.sleep, clock=clock.now)


DOWN = ("GET", "/api/v1/app/version", 0, ConnectionRefusedError())
UP = ("GET", "/api/v1/app/version", 200, {"version": "5.1.0"})


def test_version_up():
    assert make([UP]).version() == "5.1.0"


def test_version_down():
    assert make([DOWN]).version() is None


def test_ensure_running_starts_server(tmp_path):
    spawned = []
    c = make([DOWN, DOWN, UP])
    assert c.ensure_running(["invokeai-web"], tmp_path / "log", spawn=lambda cmd, log: spawned.append(cmd)) == "5.1.0"
    assert spawned == [["invokeai-web"]]


def test_ensure_running_gives_up(tmp_path):
    c = make([DOWN, DOWN, DOWN])
    with pytest.raises(InvokeError, match="within 4s"):
        c.ensure_running(["x"], tmp_path / "log", timeout=4, spawn=lambda *a: None)


def test_ensure_running_skips_spawn_when_up(tmp_path):
    c = make([UP])
    assert c.ensure_running(["x"], tmp_path / "log", spawn=lambda *a: pytest.fail("spawned")) == "5.1.0"


def test_auth_error_explained():
    with pytest.raises(InvokeError, match="single-user"):
        make([("GET", "/api/v2/models/i/k", 401, b"")]).model("k")


def test_model_not_installed():
    with pytest.raises(InvokeError, match="not installed"):
        make([("GET", "/api/v2/models/i/k", 404, b"{}")]).model("k")


def test_model_identifier():
    cfg = {"key": "k", "hash": "h", "name": "Jugg", "base": "sdxl", "type": "main", "path": "/x", "format": "diffusers"}
    assert make([("GET", "/api/v2/models/i/k", 200, cfg)]).model("k") == {
        "key": "k", "hash": "h", "name": "Jugg", "base": "sdxl", "type": "main",
    }


def test_board_existing():
    c = make([("GET", "/api/v1/boards/?all=true", 200, [{"board_id": "b9", "board_name": "Fly Trap"}])])
    assert c.board_id("Fly Trap") == "b9"


def test_board_created():
    c = make([
        ("GET", "/api/v1/boards/?all=true", 200, []),
        ("POST", "/api/v1/boards/?board_name=Fly+Trap", 201, {"board_id": "new"}),
    ])
    assert c.board_id("Fly Trap") == "new"


def test_enqueue():
    c = make([("POST", "/api/v1/queue/default/enqueue_batch", 200, {"item_ids": [31], "batch": {}})])
    assert c.enqueue({"id": "g", "nodes": {}, "edges": []}) == [31]
    body = json.loads(c.transport.calls[0][2])
    assert body == {
        "batch": {"graph": {"id": "g", "nodes": {}, "edges": []}, "runs": 1, "origin": "invoke-image"},
        "prepend": False,
    }


def test_wait_completed():
    c = make([
        ("GET", "/queue/default/i/7", 200, {"item_id": 7, "status": "pending"}),
        ("GET", "/queue/default/i/7", 200, {"item_id": 7, "status": "completed", "session": {}}),
    ])
    assert c.wait(7, timeout=60)["status"] == "completed"


def test_wait_failed_verbatim():
    failed = {"item_id": 7, "status": "failed", "error_type": "OutOfMemoryError", "error_message": "MPS backend out of memory"}
    c = make([("GET", "/queue/default/i/7", 200, failed)])
    with pytest.raises(QueueItemFailed, match="MPS backend out of memory") as exc:
        c.wait(7, timeout=60)
    assert exc.value.item["error_type"] == "OutOfMemoryError"


def test_wait_timeout_counts_running_time_and_cancels():
    pending = ("GET", "/queue/default/i/7", 200, {"item_id": 7, "status": "pending"})
    running = ("GET", "/queue/default/i/7", 200, {"item_id": 7, "status": "in_progress"})
    c = make([pending] * 3 + [running] * 6 + [("PUT", "/queue/default/i/7/cancel", 200, {})])
    with pytest.raises(InvokeError, match="longer than 10s"):
        c.wait(7, timeout=10, poll=2)
    assert c.transport.steps == []


def test_wait_stalled_queue_canceled():
    pending = ("GET", "/queue/default/i/7", 200, {"item_id": 7, "status": "pending"})
    c = make([pending] * 4 + [("PUT", "/queue/default/i/7/cancel", 200, {})])
    with pytest.raises(InvokeError, match="paused"):
        c.wait(7, timeout=10, poll=2, pending_limit=6)
    assert c.transport.steps == []


def test_wait_canceled_elsewhere():
    c = make([("GET", "/queue/default/i/7", 200, {"item_id": 7, "status": "canceled"})])
    with pytest.raises(InvokeError, match="canceled"):
        c.wait(7, timeout=10)


def test_download(tmp_path):
    c = make([("GET", "/api/v1/images/i/a.png/full", 200, b"\x89PNGdata")])
    c.download("a.png", tmp_path / "out.png")
    assert (tmp_path / "out.png").read_bytes() == b"\x89PNGdata"


def test_create_preset_multipart():
    c = make([("POST", "/api/v1/style_presets/", 200, {"id": "p1"})])
    c.create_preset("invoke-image photo", "{prompt}, photograph", "blurry")
    _, _, body, headers = c.transport.calls[0]
    assert headers["Content-Type"].startswith("multipart/form-data; boundary=")
    assert b'name="data"' in body and b'"positive_prompt": "{prompt}, photograph"' in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_client.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'invoke_image.client'`

- [ ] **Step 3: Write minimal implementation**

`scripts/invoke_image/client.py`:

```python
"""Minimal InvokeAI REST client. Transport, sleep, and clock are injectable for tests."""
import json
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

DEFAULT_BASE = "http://127.0.0.1:9090"
QUEUE = "default"


class InvokeError(Exception):
    pass


class HTTPStatusError(InvokeError):
    def __init__(self, method, path, status, body):
        self.status = status
        super().__init__(f"{method} {path} -> HTTP {status}: {body[:500].decode(errors='replace')}")


class QueueItemFailed(InvokeError):
    def __init__(self, item):
        self.item = item
        super().__init__(
            f"queue item {item.get('item_id')} failed: {item.get('error_type')}: {item.get('error_message')}"
        )


def urllib_transport(method, url, body=None, headers=None):
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def spawn_server(cmd, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = open(log_path, "ab")
    args = [str(Path(part).expanduser()) if part.startswith("~") else part for part in cmd]
    subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)


def multipart(fields):
    boundary = uuid.uuid4().hex
    parts = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'
        for key, value in fields.items()
    ]
    parts.append(f"--{boundary}--\r\n")
    return "".join(parts).encode(), {"Content-Type": f"multipart/form-data; boundary={boundary}"}


class Client:
    def __init__(self, base=DEFAULT_BASE, transport=urllib_transport, sleep=time.sleep, clock=time.monotonic):
        self.base = base.rstrip("/")
        self.transport = transport
        self.sleep = sleep
        self.clock = clock

    def request(self, method, path, payload=None, query=None, raw_body=None, headers=None):
        url = self.base + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        body, hdrs = raw_body, dict(headers or {})
        if payload is not None:
            body = json.dumps(payload).encode()
            hdrs["Content-Type"] = "application/json"
        status, data = self.transport(method, url, body, hdrs)
        if status == 401:
            raise InvokeError("InvokeAI answered 401: multi-user auth is on; invoke-image supports single-user mode only")
        if status >= 400:
            raise HTTPStatusError(method, path, status, data)
        return data

    def call(self, method, path, payload=None, query=None, raw_body=None, headers=None):
        data = self.request(method, path, payload, query, raw_body, headers)
        return json.loads(data) if data else None

    def version(self):
        try:
            return self.call("GET", "/api/v1/app/version")["version"]
        except OSError:
            return None

    def ensure_running(self, start_cmd, log_path, timeout=120, spawn=None):
        current = self.version()
        if current:
            return current
        (spawn or spawn_server)(start_cmd, Path(log_path))
        deadline = self.clock() + timeout
        while self.clock() < deadline:
            self.sleep(2)
            current = self.version()
            if current:
                return current
        raise InvokeError(f"InvokeAI did not answer within {timeout}s; see {log_path}")

    def model(self, key):
        try:
            config = self.call("GET", f"/api/v2/models/i/{urllib.parse.quote(key)}")
        except HTTPStatusError as exc:
            if exc.status == 404:
                raise InvokeError(
                    f"model {key!r} is not installed in InvokeAI; install it from the Model Manager "
                    "using the source recorded in models.json"
                ) from exc
            raise
        return {field: config[field] for field in ("key", "hash", "name", "base", "type")}

    def board_id(self, name):
        for board in self.call("GET", "/api/v1/boards/", query={"all": "true"}):
            if board["board_name"] == name:
                return board["board_id"]
        return self.call("POST", "/api/v1/boards/", query={"board_name": name})["board_id"]

    def board_image_names(self, board_id):
        names = self.call("GET", f"/api/v1/boards/{board_id}/image_names")
        return names if isinstance(names, list) else names.get("image_names", [])

    def enqueue(self, graph):
        batch = {"graph": graph, "runs": 1, "origin": "invoke-image"}
        result = self.call("POST", f"/api/v1/queue/{QUEUE}/enqueue_batch", {"batch": batch, "prepend": False})
        return result["item_ids"]

    def _cancel(self, item_id):
        self.request("PUT", f"/api/v1/queue/{QUEUE}/i/{item_id}/cancel")

    def wait(self, item_id, timeout, poll=2.0, pending_limit=1800):
        started = self.clock()
        running_since = None
        while True:
            item = self.call("GET", f"/api/v1/queue/{QUEUE}/i/{item_id}")
            status = item["status"]
            if status == "completed":
                return item
            if status == "failed":
                raise QueueItemFailed(item)
            if status == "canceled":
                raise InvokeError(f"queue item {item_id} was canceled outside invoke-image")
            now = self.clock()
            if status == "in_progress" and running_since is None:
                running_since = now
            if running_since is not None and now - running_since >= timeout:
                self._cancel(item_id)
                raise InvokeError(f"queue item {item_id} ran longer than {timeout:.0f}s; canceled")
            if running_since is None and now - started >= pending_limit:
                self._cancel(item_id)
                raise InvokeError(
                    f"queue item {item_id} still pending after {pending_limit}s; is the queue paused? canceled"
                )
            self.sleep(poll)

    def image_dto(self, name):
        return self.call("GET", f"/api/v1/images/i/{urllib.parse.quote(name)}")

    def download(self, name, dest):
        dest = Path(dest)
        dest.write_bytes(self.request("GET", f"/api/v1/images/i/{urllib.parse.quote(name)}/full"))
        return dest

    def list_presets(self):
        return self.call("GET", "/api/v1/style_presets/")

    def _preset_fields(self, name, positive, negative):
        return {"name": name, "positive_prompt": positive, "negative_prompt": negative, "type": "user"}

    def create_preset(self, name, positive, negative):
        body, headers = multipart({"data": json.dumps(self._preset_fields(name, positive, negative))})
        return self.call("POST", "/api/v1/style_presets/", raw_body=body, headers=headers)

    def update_preset(self, preset_id, name, positive, negative):
        body, headers = multipart(
            {"data": json.dumps(self._preset_fields(name, positive, negative)), "preserve_image": "true"}
        )
        return self.call("PATCH", f"/api/v1/style_presets/i/{preset_id}", raw_body=body, headers=headers)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_client.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/invoke-image/scripts/invoke_image/client.py skills/invoke-image/tests/test_client.py
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add InvokeAI REST client"
```

---

### Task 6: Runner and CLI (`gen`, `status`, `start`, dry-run)

**Files:**
- Create: `skills/invoke-image/scripts/invoke_image/runner.py`
- Create: `skills/invoke-image/scripts/invoke.py`
- Create: `skills/invoke-image/tests/fixtures/skill/models.json`
- Create: `skills/invoke-image/tests/fixtures/skill/genres/test-photo.json`
- Create: `skills/invoke-image/tests/fixtures/skill/graphs/sdxl.json`
- Test: `skills/invoke-image/tests/test_runner.py`, `skills/invoke-image/tests/test_cli.py`

**Interfaces:**
- Consumes: `sizing.dimensions`, `sizing.scaled` (Task 1); `styles.*` (Task 2); `output.*` (Task 3); `graph.fill`, `graph.load_template`, `graph.output_image_names`, `graph.GraphError` (Task 4); `Client`, `InvokeError`, `QueueItemFailed` (Task 5).
- Produces:
  - `runner.Job` dataclass: `genre, prompt, subject, model_name, model_entry, width, height, steps, cfg, board, out_dir, draft=False, loras=[], brand_client=None`
  - `runner.draft_steps(steps: int) -> int`
  - `runner.template_name(job) -> str`
  - `runner.timeout_for(entry: dict, width: int, height: int) -> float`
  - `runner.is_oom(item: dict) -> bool`
  - `runner.build_values(job, seed, width, height, model_id: dict, board_id: str) -> dict`
  - `runner.render(client, template, job, seed, model_id, board_id) -> (item, width, height, retry_note)`
  - `runner.final_image(client, item) -> str`
  - `runner.generate(client, job, template, seeds, invoke_version, clock=time.monotonic)` yields `{"path", "seed", "seconds", "model", "retry"}`
  - `invoke.main(argv: list[str] | None) -> int`, `invoke.check_version(actual, registry, accept)`, `invoke.VersionMismatch`, `invoke.load_registry(skill_dir)`, `invoke.connect(registry, accept_version) -> (Client, str)`, `invoke.SKILL_DIR`, `invoke.LOG_PATH`

- [ ] **Step 1: Create the CLI test fixtures**

`tests/fixtures/skill/models.json`:

```json
{
  "invokeai_version": "9.9.9",
  "server": {"start": ["/usr/bin/false"]},
  "models": {
    "test-sdxl": {"invoke_key": "k-sdxl", "family": "sdxl", "template": "sdxl", "source": "test", "license": "openrail++", "commercial_ok": true, "benchmark_steps": 30, "benchmark_cfg": 5.0, "seconds_1024": 10},
    "test-nc": {"invoke_key": "k-nc", "family": "sdxl", "template": "sdxl", "source": "test", "license": "cc-by-nc-4.0", "commercial_ok": false, "benchmark_steps": 30, "benchmark_cfg": 5.0, "seconds_1024": null}
  },
  "loras": {},
  "upscaler": {"invoke_key": "k-up", "source": "test", "license": "BSD-3-Clause", "commercial_ok": true, "factor": 2, "seconds_1024": null}
}
```

`tests/fixtures/skill/genres/test-photo.json`:

```json
{
  "name": "test-photo",
  "model": "test-sdxl",
  "allowed_models": ["test-sdxl", "test-nc"],
  "positive": "{subject}, photograph, {brand}",
  "negative": "blurry",
  "steps": 30,
  "cfg": 5.0
}
```

`tests/fixtures/skill/graphs/sdxl.json`:

```json
{
  "id": "fixture",
  "nodes": {
    "pos": {"id": "pos", "type": "sdxl_compel_prompt", "prompt": "{{positive}}"},
    "neg": {"id": "neg", "type": "sdxl_compel_prompt", "prompt": "{{negative}}"},
    "noise": {"id": "noise", "type": "noise", "seed": "{{seed}}", "width": "{{width}}", "height": "{{height}}"},
    "denoise": {"id": "denoise", "type": "denoise_latents", "steps": "{{steps}}", "cfg_scale": "{{cfg}}"},
    "model": {"id": "model", "type": "sdxl_model_loader", "model": "{{model}}"},
    "l2i": {"id": "l2i", "type": "l2i", "board": "{{board}}", "is_intermediate": false}
  },
  "edges": []
}
```

- [ ] **Step 2: Write the failing runner test**

`tests/test_runner.py`:

```python
import json
from pathlib import Path

import pytest

from invoke_image import runner, styles
from invoke_image.client import InvokeError, QueueItemFailed

TEMPLATE = {
    "id": "t",
    "nodes": {
        "pos": {"prompt": "{{positive}}"},
        "noise": {"seed": "{{seed}}", "width": "{{width}}", "height": "{{height}}"},
        "d": {"steps": "{{steps}}", "cfg": "{{cfg}}"},
        "m": {"model": "{{model}}"},
        "out": {"board": "{{board}}"},
    },
    "edges": [],
}
ENTRY = {"invoke_key": "k-sdxl", "family": "sdxl", "template": "sdxl", "license": "openrail++",
         "commercial_ok": True, "seconds_1024": 10}


class FakeClient:
    def __init__(self, fail=None, only_intermediate=False):
        self.fail = fail or {}
        self.only_intermediate = only_intermediate
        self.enqueued, self.downloads, self.timeouts = [], [], []

    def model(self, key):
        return {"key": key, "hash": "h", "name": "n", "base": "sdxl", "type": "main"}

    def board_id(self, name):
        return "b1"

    def enqueue(self, graph):
        self.enqueued.append(graph)
        return [len(self.enqueued)]

    def wait(self, item_id, timeout):
        self.timeouts.append(timeout)
        if item_id in self.fail:
            raise QueueItemFailed({"item_id": item_id, "status": "failed", "error_type": "RuntimeError",
                                   "error_message": self.fail[item_id]})
        results = {"a": {"type": "image_output", "image": {"image_name": f"inter-{item_id}.png"}}}
        if not self.only_intermediate:
            results["b"] = {"type": "image_output", "image": {"image_name": f"final-{item_id}.png"}}
        return {"item_id": item_id, "status": "completed", "session": {"results": results}}

    def image_dto(self, name):
        return {"image_name": name, "is_intermediate": name.startswith("inter")}

    def download(self, name, dest):
        Path(dest).write_bytes(b"PNG")
        self.downloads.append(name)


def make_job(tmp_path, **overrides):
    genre = styles.Genre(name="photo", model="m", allowed_models=["m"], positive="{subject}",
                         negative="blurry", steps=30, cfg=5.0)
    fields = dict(genre=genre, prompt=styles.Prompt("pancakes", "blurry"), subject="Pancakes!",
                  model_name="m", model_entry=ENTRY, width=1344, height=768, steps=30, cfg=5.0,
                  board="Fly Trap", out_dir=tmp_path, brand_client="Fly Trap")
    fields.update(overrides)
    return runner.Job(**fields)


def test_draft_steps():
    assert [runner.draft_steps(s) for s in (30, 20, 10, 4)] == [12, 8, 8, 4]


def test_timeout_for():
    assert runner.timeout_for({"seconds_1024": None}, 1024, 1024) == 900.0
    assert runner.timeout_for({"seconds_1024": 10}, 1024, 1024) == 30.0


def test_template_name(tmp_path):
    job = make_job(tmp_path)
    assert runner.template_name(job) == "sdxl"
    job.genre.template_suffix = "-seamless"
    assert runner.template_name(job) == "sdxl-seamless"
    job.loras = [("l", {}, 0.7)]
    assert runner.template_name(job) == "sdxl-seamless-lora"


def test_is_oom():
    assert runner.is_oom({"error_type": "RuntimeError", "error_message": "MPS backend out of memory"})
    assert not runner.is_oom({"error_type": "KeyError", "error_message": "'unet'"})


def test_generate_writes_final_image_and_sidecar(tmp_path):
    client = FakeClient()
    ticks = iter(range(100))
    results = list(runner.generate(client, make_job(tmp_path), TEMPLATE, [11, 22], "5.0.0",
                                   clock=lambda: next(ticks)))
    assert [r["seed"] for r in results] == [11, 22]
    assert client.downloads == ["final-1.png", "final-2.png"]
    png = tmp_path / "pancakes-photo-11.png"
    assert png.read_bytes() == b"PNG"
    side = json.loads(png.with_suffix(".json").read_text())
    assert side["seed"] == 11 and side["width"] == 1344 and side["client"] == "Fly Trap"
    assert side["commercial_ok"] is True and side["invoke_image_name"] == "final-1.png"
    assert side["retry"] is None and side["invokeai_version"] == "5.0.0"
    first, second = client.enqueued
    assert first["nodes"]["noise"]["seed"] == 11
    assert first["nodes"]["out"]["board"] == {"board_id": "b1"}
    assert first["id"] != second["id"]
    assert client.timeouts[0] == pytest.approx(3 * 10 * 1344 * 768 / 1048576)


def test_draft_filename(tmp_path):
    list(runner.generate(FakeClient(), make_job(tmp_path, draft=True, steps=12), TEMPLATE, [5], "5.0.0"))
    assert (tmp_path / "pancakes-photo-5-draft.png").exists()


def test_oom_retries_once_at_smaller_size(tmp_path):
    client = FakeClient(fail={1: "MPS backend out of memory (MPS allocated: 15 GB)"})
    [result] = list(runner.generate(client, make_job(tmp_path), TEMPLATE, [7], "5.0.0"))
    assert len(client.enqueued) == 2
    assert client.enqueued[1]["nodes"]["noise"]["width"] == 1024
    assert client.enqueued[1]["nodes"]["noise"]["height"] == 576
    assert "retried once at 1024x576" in result["retry"]
    side = json.loads((tmp_path / "pancakes-photo-7.json").read_text())
    assert (side["width"], side["height"]) == (1024, 576)


def test_oom_twice_raises(tmp_path):
    client = FakeClient(fail={1: "out of memory", 2: "out of memory"})
    with pytest.raises(QueueItemFailed):
        list(runner.generate(client, make_job(tmp_path), TEMPLATE, [7], "5.0.0"))
    assert len(client.enqueued) == 2


def test_non_oom_failure_not_retried(tmp_path):
    client = FakeClient(fail={1: "KeyError: 'unet'"})
    with pytest.raises(QueueItemFailed, match="unet"):
        list(runner.generate(client, make_job(tmp_path), TEMPLATE, [7], "5.0.0"))
    assert len(client.enqueued) == 1


def test_no_saved_image_raises(tmp_path):
    with pytest.raises(InvokeError, match="non-intermediate"):
        list(runner.generate(FakeClient(only_intermediate=True), make_job(tmp_path), TEMPLATE, [7], "5.0.0"))
```

- [ ] **Step 3: Write the failing CLI test**

`tests/test_cli.py`:

```python
import json
from pathlib import Path

import pytest

import invoke

FIXTURE = Path(__file__).parent / "fixtures" / "skill"


def run(capsys, *argv):
    code = invoke.main(["--skill-dir", str(FIXTURE), *argv])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def add_brand(repo):
    (repo / ".claude").mkdir()
    (repo / ".claude" / "image-brand.json").write_text(
        json.dumps({"client": "Fly Trap", "brand": "diner red", "avoid": ["text"]})
    )


def test_dry_run_without_brand(repo, capsys):
    code, out, _ = run(capsys, "gen", "--genre", "test-photo", "--subject", "red apple", "--seed", "5", "--dry-run")
    assert code == 0
    nodes = json.loads(out)["graph"]["nodes"]
    assert nodes["pos"]["prompt"] == "red apple, photograph"
    assert nodes["noise"] == {"id": "noise", "type": "noise", "seed": 5, "width": 1024, "height": 1024}
    assert nodes["model"]["model"] == {"key": "k-sdxl"}
    assert nodes["l2i"]["board"] == {"board_id": "dry-run"}
    assert not (repo / "generated").exists()


def test_dry_run_draft_and_aspect(repo, capsys):
    code, out, _ = run(capsys, "gen", "--genre", "test-photo", "--subject", "x", "--seed", "1",
                       "--aspect", "16:9", "--draft", "--dry-run")
    data = json.loads(out)
    assert code == 0 and (data["width"], data["height"], data["steps"]) == (1344, 768, 12)


def test_dry_run_with_brand(repo, capsys):
    add_brand(repo)
    code, out, _ = run(capsys, "gen", "--genre", "test-photo", "--subject", "pie", "--seed", "1", "--dry-run")
    data = json.loads(out)
    assert code == 0
    assert data["positive"] == "pie, photograph, diner red"
    assert data["negative"] == "blurry, text"


def test_noncommercial_model_refused_for_brand(repo, capsys):
    add_brand(repo)
    code, _, err = run(capsys, "gen", "--genre", "test-photo", "--subject", "pie", "--model", "test-nc", "--dry-run")
    assert code == 2 and "cc-by-nc-4.0" in err


def test_noncommercial_model_allowed_without_brand(repo, capsys):
    code, _, _ = run(capsys, "gen", "--genre", "test-photo", "--subject", "pie", "--model", "test-nc",
                     "--seed", "1", "--dry-run")
    assert code == 0


def test_bad_aspect_exit_2(repo, capsys):
    code, _, err = run(capsys, "gen", "--genre", "test-photo", "--subject", "pie", "--aspect", "5:4", "--dry-run")
    assert code == 2 and "16:9" in err


def test_unknown_genre_exit_2(repo, capsys):
    code, _, err = run(capsys, "gen", "--genre", "nope", "--subject", "pie", "--dry-run")
    assert code == 2 and "test-photo" in err


def test_version_gate():
    with pytest.raises(invoke.VersionMismatch, match="9.9.9"):
        invoke.check_version("5.0.0", {"invokeai_version": "9.9.9"}, accept=False)
    invoke.check_version("5.0.0", {"invokeai_version": "9.9.9"}, accept=True)
```

- [ ] **Step 4: Run both tests to verify they fail**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_runner.py tests/test_cli.py -q`
Expected: FAIL with `ImportError: cannot import name 'runner'` and `ModuleNotFoundError: No module named 'invoke'`

- [ ] **Step 5: Write the runner**

`scripts/invoke_image/runner.py`:

```python
"""Render jobs through InvokeAI: fill graph, enqueue, wait, retry once on OOM, save."""
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from . import graph, output, sizing
from .client import InvokeError, QueueItemFailed


@dataclass
class Job:
    genre: object
    prompt: object
    subject: str
    model_name: str
    model_entry: dict
    width: int
    height: int
    steps: int
    cfg: float
    board: str
    out_dir: Path
    draft: bool = False
    loras: list = field(default_factory=list)
    brand_client: str | None = None


def draft_steps(steps):
    return steps if steps <= 8 else max(8, round(steps * 0.4))


def template_name(job):
    return job.model_entry["template"] + job.genre.template_suffix + ("-lora" if job.loras else "")


def timeout_for(entry, width, height):
    base = entry.get("seconds_1024")
    if not base:
        return 900.0
    return 3.0 * base * (width * height) / (1024 * 1024)


def is_oom(item):
    text = f"{item.get('error_type') or ''} {item.get('error_message') or ''}".lower()
    return "out of memory" in text


def build_values(job, seed, width, height, model_id, board_id):
    return {
        "positive": job.prompt.positive,
        "negative": job.prompt.negative,
        "seed": seed,
        "width": width,
        "height": height,
        "steps": job.steps,
        "cfg": job.cfg,
        "model": model_id,
        "board": {"board_id": board_id},
    }


def render(client, template, job, seed, model_id, board_id):
    width, height, note = job.width, job.height, None
    while True:
        filled = graph.fill(template, build_values(job, seed, width, height, model_id, board_id))
        filled["id"] = str(uuid.uuid4())
        item_id = client.enqueue(filled)[0]
        try:
            return client.wait(item_id, timeout_for(job.model_entry, width, height)), width, height, note
        except QueueItemFailed as exc:
            if note is not None or not is_oom(exc.item):
                raise
            width, height = sizing.scaled(width, height, 0.75, job.model_entry["family"])
            note = f"out of memory at {job.width}x{job.height}; retried once at {width}x{height}"


def final_image(client, item):
    for name in reversed(graph.output_image_names(item)):
        if not client.image_dto(name).get("is_intermediate"):
            return name
    raise InvokeError(f"queue item {item.get('item_id')} completed without a saved non-intermediate image")


def generate(client, job, template, seeds, invoke_version, clock=time.monotonic):
    model_id = client.model(job.model_entry["invoke_key"])
    board_id = client.board_id(job.board)
    slug = output.slugify(job.subject)
    for seed in seeds:
        started = clock()
        item, width, height, note = render(client, template, job, seed, model_id, board_id)
        name = final_image(client, item)
        path = output.output_path(job.out_dir, slug, job.genre.name, seed, suffix="-draft" if job.draft else "")
        client.download(name, path)
        output.write_sidecar(path, {
            "subject": job.subject,
            "genre": job.genre.name,
            "client": job.brand_client,
            "model": job.model_name,
            "invoke_key": job.model_entry["invoke_key"],
            "license": job.model_entry.get("license"),
            "commercial_ok": job.model_entry.get("commercial_ok", False),
            "loras": [{"key": key, "weight": weight, "license": entry.get("license")} for key, entry, weight in job.loras],
            "positive": job.prompt.positive,
            "negative": job.prompt.negative,
            "seed": seed,
            "steps": job.steps,
            "cfg": job.cfg,
            "width": width,
            "height": height,
            "draft": job.draft,
            "retry": note,
            "invokeai_version": invoke_version,
            "invoke_image_name": name,
        })
        yield {"path": str(path), "seed": seed, "seconds": round(clock() - started, 1),
               "model": job.model_name, "retry": note}
```

- [ ] **Step 6: Write the CLI**

`scripts/invoke.py`:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["vtracer"]
# ///
"""invoke-image CLI: drive a local InvokeAI to render brand-consistent images."""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from invoke_image import graph, output, runner, sizing, styles  # noqa: E402
from invoke_image.client import Client, InvokeError  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parents[1]
LOG_PATH = Path.home() / ".cache" / "invoke-image" / "server.log"


class VersionMismatch(Exception):
    pass


def load_registry(skill_dir):
    return json.loads((Path(skill_dir) / "models.json").read_text())


def check_version(actual, registry, accept):
    pinned = registry.get("invokeai_version")
    if actual != pinned and not accept:
        raise VersionMismatch(
            f"InvokeAI is {actual} but graph templates were captured on {pinned}. "
            "Recapture the templates, or rerun with --accept-version after the user confirms."
        )


def connect(registry, accept_version):
    client = Client()
    version = client.ensure_running(registry["server"]["start"], LOG_PATH)
    check_version(version, registry, accept_version)
    return client, version


def cmd_status(args):
    registry = load_registry(args.skill_dir)
    client = Client()
    version = client.version()
    print(f"server: {'up ' + version if version else 'down'}")
    print(f"pinned version: {registry.get('invokeai_version')}")
    if not version:
        return 0
    for name, entry in sorted(registry["models"].items()):
        try:
            client.model(entry["invoke_key"])
            state = "installed"
        except InvokeError as exc:
            state = f"MISSING ({exc})"
        print(f"model {name}: {state}")
    return 0


def cmd_start(args):
    registry = load_registry(args.skill_dir)
    print(Client().ensure_running(registry["server"]["start"], LOG_PATH))
    return 0


def cmd_gen(args):
    skill = Path(args.skill_dir)
    registry = load_registry(skill)
    genre = styles.load_genre(skill / "genres", args.genre)
    brand = styles.find_brand(Path.cwd())
    model_name, entry = styles.resolve_model(genre, registry, args.model)
    loras = styles.resolve_loras(genre, registry)
    styles.check_license([(model_name, entry)] + [(key, lora) for key, lora, _ in loras], brand)
    prompt = styles.merge(genre, args.subject, brand)
    width, height = sizing.dimensions(args.aspect, entry["family"])
    job = runner.Job(
        genre=genre, prompt=prompt, subject=args.subject, model_name=model_name, model_entry=entry,
        width=width, height=height,
        steps=runner.draft_steps(genre.steps) if args.draft else genre.steps, cfg=genre.cfg,
        board=brand.client if brand else "invoke-image",
        out_dir=Path.cwd() if args.dry_run else output.resolve_output_dir(brand, Path.cwd()),
        draft=args.draft, loras=loras, brand_client=brand.client if brand else None,
    )
    template = graph.load_template(skill / "graphs", runner.template_name(job))
    seeds = args.seed or [random.randrange(2**31) for _ in range(args.n)]
    if args.dry_run:
        values = runner.build_values(job, seeds[0], width, height, {"key": entry["invoke_key"]}, "dry-run")
        print(json.dumps({
            "seeds": seeds, "positive": prompt.positive, "negative": prompt.negative,
            "width": width, "height": height, "steps": job.steps, "graph": graph.fill(template, values),
        }, indent=2))
        return 0
    client, version = connect(registry, args.accept_version)
    for result in runner.generate(client, job, template, seeds, version):
        print(json.dumps(result), flush=True)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="invoke.py")
    parser.add_argument("--skill-dir", default=str(SKILL_DIR))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("start").set_defaults(func=cmd_start)

    gen = sub.add_parser("gen")
    gen.add_argument("--genre", required=True)
    gen.add_argument("--subject", required=True)
    gen.add_argument("--aspect", default="1:1")
    gen.add_argument("--n", type=int, default=4)
    gen.add_argument("--seed", type=int, action="append")
    gen.add_argument("--model")
    gen.add_argument("--draft", action="store_true")
    gen.add_argument("--dry-run", action="store_true")
    gen.add_argument("--accept-version", action="store_true")
    gen.set_defaults(func=cmd_gen)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (styles.StyleError, graph.GraphError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except VersionMismatch as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except InvokeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 7: Run all tests to verify they pass**

Run: `cd skills/invoke-image && chmod +x scripts/invoke.py && uv run --python 3.13 --with pytest --with vtracer pytest tests -q`
Expected: PASS (all tests from Tasks 1 to 6)

- [ ] **Step 8: Commit**

```bash
git add skills/invoke-image
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add runner and gen CLI with dry-run"
```

---

### Task 7: Install InvokeAI and starter models; write `models.json`

This task needs the user. Downloading the Launcher is a file download, so ask the user to do it (or get an explicit yes first).

**Files:**
- Create: `skills/invoke-image/models.json`
- Test: `skills/invoke-image/tests/test_registry.py`

**Interfaces:**
- Produces: `models.json` with keys `invokeai_version`, `server.start`, `models.<name>` (`invoke_key, family, template, source, license, commercial_ok, benchmark_steps, benchmark_cfg, seconds_1024`), `loras`, `upscaler` (`invoke_key, source, license, commercial_ok, factor, seconds_1024`). Model names used by later tasks: `juggernaut-xl`, `sdxl-base`, `flux-schnell`, `flux-dev`.

- [ ] **Step 1: Write the failing registry test**

`tests/test_registry.py`:

```python
import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "models.json"
REQUIRED = {"invoke_key", "family", "template", "source", "license", "commercial_ok",
            "benchmark_steps", "benchmark_cfg", "seconds_1024"}


def test_registry_complete():
    data = json.loads(REGISTRY.read_text())
    assert data["invokeai_version"]
    assert "<" not in json.dumps(data), "unfilled <...> value in models.json"
    assert data["server"]["start"]
    assert {"juggernaut-xl", "sdxl-base", "flux-schnell", "flux-dev"} <= data["models"].keys()
    for name, entry in data["models"].items():
        assert REQUIRED <= entry.keys(), name
        assert entry["family"] in ("sdxl", "flux"), name
        assert isinstance(entry["commercial_ok"], bool), name
    assert {"invoke_key", "source", "license", "commercial_ok", "factor"} <= data["upscaler"].keys()
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_registry.py -q`
Expected: FAIL with `FileNotFoundError` for `models.json`

- [ ] **Step 2: User installs InvokeAI**

Ask the user to download the Launcher from https://github.com/invoke-ai/launcher/releases (macOS arm64 `.dmg`), install, choose an install folder (recommend `~/invokeai`), and click Launch. Then verify:

```bash
curl -s http://127.0.0.1:9090/api/v1/app/version
ls ~/invokeai/.venv/bin/invokeai-web
```

Expected: JSON with `"version"`, and the `invokeai-web` path exists. If the install folder differs, use that path everywhere below.

- [ ] **Step 3: Install starter models from the Model Manager**

Open `http://127.0.0.1:9090` in the in-app browser pane (local dev host; allowed). Model Manager, Starter Models tab. Install:
1. **Juggernaut XL** (SDXL)
2. **SDXL base 1.0** (`stabilityai/stable-diffusion-xl-base-1.0`)
3. **FLUX.1 schnell** in a **GGUF quantized** variant (bitsandbytes variants do not run on Apple Silicon); the Starter Models flow pulls the T5 encoder, CLIP, and FLUX VAE dependencies
4. **FLUX.1 dev** GGUF quantized (Q4 if offered, otherwise the smallest GGUF)
5. **RealESRGAN x2plus** upscaler. If it is not in Starter Models, install by URL:

```bash
curl -s -X POST 'http://127.0.0.1:9090/api/v2/models/install?source=https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth'
```

Do not install `4x-UltraSharp` (CC-BY-NC-SA, non-commercial). Watch progress in the UI until every install shows done.

- [ ] **Step 4: Inventory the installed models**

```bash
curl -s 'http://127.0.0.1:9090/api/v2/models/' | jq -r '.models[] | [.key, .name, .base, .type, .format, .source] | @tsv'
```

Expected: one row per installed model, including dependencies. Note the `key` and `source` for the five models above.

- [ ] **Step 5: Verify licenses from each model's source page**

For each of the five, open the `source` (Hugging Face card or release page) and record the license string. Rules:
- SDXL base 1.0: CreativeML OpenRAIL++-M, `commercial_ok: true`.
- FLUX.1 schnell: Apache-2.0, `commercial_ok: true`.
- FLUX.1 dev: FLUX.1 [dev] Non-Commercial License, outputs commercial OK per section 2(d) (verified 2026-10-14), `commercial_ok: true`, and put the 2(d) note in `license`.
- Juggernaut XL: read the card. If it does not clearly permit commercial use of outputs, set `commercial_ok: false` and tell the user; client genres then default to `sdxl-base`/`flux-dev` in Task 10.
- RealESRGAN: BSD-3-Clause, `commercial_ok: true`.

- [ ] **Step 6: Write `models.json`**

Replace every `<...>` with the values from Steps 2 to 5 (the registry test fails while any `<` remains):

```json
{
  "invokeai_version": "<version from /api/v1/app/version>",
  "server": {"start": ["<install>/.venv/bin/invokeai-web", "--root", "<install>"]},
  "models": {
    "juggernaut-xl": {"invoke_key": "<key>", "family": "sdxl", "template": "sdxl", "source": "<source>", "license": "<license>", "commercial_ok": false, "benchmark_steps": 30, "benchmark_cfg": 5.0, "seconds_1024": null},
    "sdxl-base": {"invoke_key": "<key>", "family": "sdxl", "template": "sdxl", "source": "<source>", "license": "CreativeML OpenRAIL++-M", "commercial_ok": true, "benchmark_steps": 30, "benchmark_cfg": 6.0, "seconds_1024": null},
    "flux-schnell": {"invoke_key": "<key>", "family": "flux", "template": "flux", "source": "<source>", "license": "Apache-2.0", "commercial_ok": true, "benchmark_steps": 4, "benchmark_cfg": 3.5, "seconds_1024": null},
    "flux-dev": {"invoke_key": "<key>", "family": "flux", "template": "flux", "source": "<source>", "license": "FLUX.1 [dev] Non-Commercial; outputs commercial OK per section 2(d)", "commercial_ok": true, "benchmark_steps": 28, "benchmark_cfg": 3.5, "seconds_1024": null}
  },
  "loras": {},
  "upscaler": {"invoke_key": "<key>", "source": "<source>", "license": "BSD-3-Clause", "commercial_ok": true, "factor": 2, "seconds_1024": null}
}
```

Set `juggernaut-xl.commercial_ok` from Step 5.

- [ ] **Step 7: Verify**

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests -q && ./scripts/invoke.py status`
Expected: tests PASS; `status` prints `server: up <version>`, matching pinned version, and `installed` for all four models.

- [ ] **Step 8: Commit**

```bash
git add skills/invoke-image/models.json skills/invoke-image/tests/test_registry.py
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add model registry for local InvokeAI"
```

---

### Task 8: Capture graph templates

**Files:**
- Modify: `skills/invoke-image/scripts/invoke.py` (add `capture` subcommand)
- Create: `skills/invoke-image/graphs/raw/{sdxl,sdxl-seamless,flux,upscale}-batch.json`
- Create: `skills/invoke-image/graphs/{sdxl,sdxl-seamless,flux,upscale}.json`
- Test: `skills/invoke-image/tests/test_cli.py` (append)

**Interfaces:**
- Consumes: `graph.collapse_batch_data`, `graph.templatize` (Task 4).
- Produces: `invoke.py capture --raw PATH --name NAME [--positive S] [--negative S] [--seed N] [--width N] [--height N] [--steps N] [--cfg F] [--model-key K] [--board-id B] [--image-name I]`; writes `graphs/<NAME>.json`; exit 2 if any given sentinel matched zero times. Template placeholders: `positive, negative (sdxl only), seed, width, height, steps, cfg, model, board` for generation templates; `image, model, board` for `upscale`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_cli.py`:

```python
def test_capture_templatizes_raw_batch(tmp_path, capsys):
    skill = tmp_path / "skill"
    (skill / "graphs").mkdir(parents=True)
    raw = {"batch": {"graph": {"id": "x", "nodes": {
        "pos": {"prompt": "XPOSX"}, "noise": {"seed": 0, "width": 1152, "height": 896},
        "m": {"model": {"key": "mk", "name": "J"}}, "out": {"board": {"board_id": "bid"}}}, "edges": []},
        "data": [[{"node_path": "noise", "field_name": "seed", "items": [424242]}]]}}
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw))
    code = invoke.main(["--skill-dir", str(skill), "capture", "--raw", str(raw_path), "--name", "sdxl",
                        "--positive", "XPOSX", "--seed", "424242", "--width", "1152", "--height", "896",
                        "--model-key", "mk", "--board-id", "bid"])
    assert code == 0
    written = json.loads((skill / "graphs" / "sdxl.json").read_text())
    assert written["nodes"]["noise"] == {"seed": "{{seed}}", "width": "{{width}}", "height": "{{height}}"}
    assert written["nodes"]["m"]["model"] == "{{model}}"


def test_capture_unmatched_sentinel_exit_2(tmp_path, capsys):
    skill = tmp_path / "skill"
    (skill / "graphs").mkdir(parents=True)
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps({"batch": {"graph": {"nodes": {"pos": {"prompt": "XPOSX"}}}}}))
    code = invoke.main(["--skill-dir", str(skill), "capture", "--raw", str(raw_path), "--name", "sdxl",
                        "--positive", "XPOSX", "--steps", "23"])
    assert code == 2 and "steps" in capsys.readouterr().err
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_cli.py -q`
Expected: FAIL with `invalid choice: 'capture'` (SystemExit 2 from argparse)

- [ ] **Step 2: Add the `capture` subcommand**

In `scripts/invoke.py`, add after `cmd_gen`:

```python
def cmd_capture(args):
    raw = json.loads(Path(args.raw).read_text())
    batch = raw.get("batch", raw)
    captured = graph.collapse_batch_data(batch)
    sentinels = {}
    for name in ("positive", "negative", "seed", "width", "height", "steps", "cfg"):
        value = getattr(args, name)
        if value is not None:
            sentinels[name] = value
    if args.model_key:
        sentinels["model"] = {"key": args.model_key}
    if args.board_id:
        sentinels["board"] = {"board_id": args.board_id}
    if args.image_name:
        sentinels["image"] = {"image_name": args.image_name}
    template, counts = graph.templatize(captured, sentinels)
    out = Path(args.skill_dir) / "graphs" / f"{args.name}.json"
    out.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"written": str(out), "replacements": counts}))
    unmatched = [name for name, count in counts.items() if count == 0]
    if unmatched:
        print(f"error: sentinel never matched: {', '.join(unmatched)}", file=sys.stderr)
        return 2
    return 0
```

In `build_parser`, before `return parser`:

```python
    cap = sub.add_parser("capture")
    cap.add_argument("--raw", required=True)
    cap.add_argument("--name", required=True)
    cap.add_argument("--positive")
    cap.add_argument("--negative")
    cap.add_argument("--seed", type=int)
    cap.add_argument("--width", type=int)
    cap.add_argument("--height", type=int)
    cap.add_argument("--steps", type=int)
    cap.add_argument("--cfg", type=float)
    cap.add_argument("--model-key")
    cap.add_argument("--board-id")
    cap.add_argument("--image-name")
    cap.set_defaults(func=cmd_capture)
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests -q`
Expected: PASS

- [ ] **Step 3: Capture the SDXL graph**

In the InvokeAI UI (in-app browser pane at `http://127.0.0.1:9090`):
1. Create a board named `capture`; set it as the auto-add board. Get its id: `curl -s 'http://127.0.0.1:9090/api/v1/boards/?all=true' | jq -r '.[] | select(.board_name=="capture") | .board_id'`
2. Generate tab. Model: Juggernaut XL. No LoRA, no style preset, no reference images.
3. Positive prompt exactly `XPOSX`. Negative exactly `XNEGX`.
4. Seed `424242` with random seed off. Width `1152`, height `896`. Steps `23`. CFG `5.5`.
5. Click Invoke. Read the request body with `read_network_requests` (urlPattern `enqueue_batch`), then `read_network_requests` with that `requestId`. Save the request JSON body to `graphs/raw/sdxl-batch.json` with the Write tool.

Then:

```bash
cd skills/invoke-image
./scripts/invoke.py capture --raw graphs/raw/sdxl-batch.json --name sdxl \
  --positive XPOSX --negative XNEGX --seed 424242 --width 1152 --height 896 \
  --steps 23 --cfg 5.5 --model-key <juggernaut invoke_key> --board-id <capture board id>
```

Expected: exit 0; every replacement count at least 1. If a sentinel shows 0, the UI stored that value elsewhere: inspect the raw file, fix the capture inputs, rerun. If a count is surprisingly high (for example `width` matching an unrelated field), inspect `graphs/sdxl.json` and hand-correct that one field back to its literal value.

- [ ] **Step 4: Capture the SDXL seamless graph**

Same as Step 3 but model SDXL base, and turn on Seamless X and Seamless Y in the generation advanced settings. Save to `graphs/raw/sdxl-seamless-batch.json`, then:

```bash
./scripts/invoke.py capture --raw graphs/raw/sdxl-seamless-batch.json --name sdxl-seamless \
  --positive XPOSX --negative XNEGX --seed 424242 --width 1152 --height 896 \
  --steps 23 --cfg 5.5 --model-key <sdxl-base invoke_key> --board-id <capture board id>
```

Expected: exit 0. Confirm the template contains a seamless node: `grep -c seamless graphs/sdxl-seamless.json` returns at least 1.

- [ ] **Step 5: Capture the FLUX graph**

Model FLUX.1 dev GGUF. Prompt `XPOSX` (FLUX has no negative prompt). Seed `424242`, width `1184`, height `880`, steps `23`, guidance `3.7`. Save to `graphs/raw/flux-batch.json`, then:

```bash
./scripts/invoke.py capture --raw graphs/raw/flux-batch.json --name flux \
  --positive XPOSX --seed 424242 --width 1184 --height 880 \
  --steps 23 --cfg 3.7 --model-key <flux-dev invoke_key> --board-id <capture board id>
```

Expected: exit 0. The `cfg` placeholder lands on the guidance field.

- [ ] **Step 6: Capture the upscale graph**

Workflow Editor. Build: an Image primitive (choose any image from the `capture` board; note its `image_name` from the image info panel) connected to the Spandrel image-to-image upscale node with model RealESRGAN x2plus, whose output saves to board `capture` (not intermediate). Invoke. Save the body to `graphs/raw/upscale-batch.json`, then:

```bash
./scripts/invoke.py capture --raw graphs/raw/upscale-batch.json --name upscale \
  --image-name <that image_name> --model-key <upscaler invoke_key> --board-id <capture board id>
```

Expected: exit 0 with `image`, `model`, `board` each at least 1.

- [ ] **Step 7: Check every template's placeholder set**

```bash
cd skills/invoke-image
for t in sdxl sdxl-seamless flux upscale; do
  uv run --python 3.13 python -c "import json,sys; sys.path.insert(0,'scripts'); from invoke_image import graph; print('$t', sorted(graph.placeholders(json.load(open('graphs/$t.json')))))"
done
```

Expected:
- `sdxl`, `sdxl-seamless`: `['board', 'cfg', 'height', 'model', 'negative', 'positive', 'seed', 'steps', 'width']`
- `flux`: the same without `negative`
- `upscale`: `['board', 'image', 'model']`

Real renders are verified by `selftest` in Task 9. Create the scratch repo used by later live checks: `mkdir -p /tmp/ii-check && git -C /tmp/ii-check init -q`.

- [ ] **Step 8: Commit**

```bash
git add skills/invoke-image/scripts/invoke.py skills/invoke-image/tests/test_cli.py skills/invoke-image/graphs
git commit -F <scratch>/msg.txt   # "feat(invoke-image): capture SDXL, seamless, FLUX and upscale graph templates"
```

---

### Task 9: Selftest, benchmark, speed gate

**Files:**
- Modify: `skills/invoke-image/scripts/invoke.py` (add `selftest`, `benchmark`)
- Modify: `skills/invoke-image/models.json` (benchmark writes `seconds_1024`)
- Test: `skills/invoke-image/tests/test_cli.py` (append)

**Interfaces:**
- Consumes: `runner.Job`, `runner.generate`, `runner.template_name`, `runner.draft_steps`, `sizing.dimensions`, `styles.Genre`, `styles.merge`, `Client.board_id`, `Client.board_image_names`, `invoke.connect`.
- Produces: `invoke.adhoc_genre(name: str, model: str, steps: int, cfg: float) -> styles.Genre`, `invoke.GATE_SECONDS = 300`, `invoke.gate_verdict(seconds: float | None) -> str`; subcommands `selftest` (exit 1 if any family fails) and `benchmark [--model NAME]`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_cli.py`:

```python
def test_adhoc_genre_is_plain():
    g = invoke.adhoc_genre("selftest", "m", 4, 3.5)
    assert g.positive == "{subject}" and g.allowed_models == ["m"] and g.steps == 4


def test_gate_verdict():
    assert invoke.gate_verdict(120.0) == "ok"
    assert invoke.gate_verdict(301.0).startswith("SLOW")
    assert invoke.gate_verdict(None).startswith("SLOW")
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_cli.py -q`
Expected: FAIL with `AttributeError: module 'invoke' has no attribute 'adhoc_genre'`

- [ ] **Step 2: Implement `selftest` and `benchmark`**

In `scripts/invoke.py`, add after `cmd_capture`:

```python
GATE_SECONDS = 300
SELFTEST_SUBJECT = "a red apple on a white table, studio light"
CACHE_DIR = Path.home() / ".cache" / "invoke-image"


def adhoc_genre(name, model, steps, cfg):
    return styles.Genre(name=name, model=model, allowed_models=[model], positive="{subject}",
                        negative="blurry, watermark", steps=steps, cfg=cfg)


def gate_verdict(seconds):
    if seconds is None or seconds > GATE_SECONDS:
        return f"SLOW: over the {GATE_SECONDS}s gate; remove from genre defaults"
    return "ok"


def _job(name, entry, genre, width, height, steps, board, out_dir, draft):
    return runner.Job(genre=genre, prompt=styles.merge(genre, SELFTEST_SUBJECT), subject=SELFTEST_SUBJECT,
                      model_name=name, model_entry=entry, width=width, height=height, steps=steps,
                      cfg=genre.cfg, board=board, out_dir=out_dir, draft=draft)


def cmd_selftest(args):
    skill = Path(args.skill_dir)
    registry = load_registry(skill)
    client, version = connect(registry, args.accept_version)
    out_dir = CACHE_DIR / "selftest"
    out_dir.mkdir(parents=True, exist_ok=True)
    board = "invoke-image-selftest"
    failures, seen = 0, set()
    for name, entry in sorted(registry["models"].items()):
        if entry["family"] in seen:
            continue
        seen.add(entry["family"])
        genre = adhoc_genre("selftest", name, entry["benchmark_steps"], entry["benchmark_cfg"])
        width, height = sizing.dimensions("1:1", entry["family"], area=512 * 512)
        job = _job(name, entry, genre, width, height, runner.draft_steps(genre.steps), board, out_dir, True)
        template = graph.load_template(skill / "graphs", runner.template_name(job))
        [result] = list(runner.generate(client, job, template, [1234], version))
        path = Path(result["path"])
        side = json.loads(path.with_suffix(".json").read_text())
        ok = (path.stat().st_size > 1000
              and side["invoke_image_name"] in client.board_image_names(client.board_id(board)))
        failures += not ok
        print(json.dumps({"family": entry["family"], "ok": ok, **result}), flush=True)
    return 1 if failures else 0


def cmd_benchmark(args):
    skill = Path(args.skill_dir)
    registry = load_registry(skill)
    client, version = connect(registry, args.accept_version)
    out_dir = CACHE_DIR / "benchmark"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, entry in sorted(registry["models"].items()):
        if args.model and name != args.model:
            continue
        genre = adhoc_genre("benchmark", name, entry["benchmark_steps"], entry["benchmark_cfg"])
        probe = dict(entry, seconds_1024=None)
        template = graph.load_template(skill / "graphs", entry["template"])
        warm_w, warm_h = sizing.dimensions("1:1", entry["family"], area=512 * 512)
        list(runner.generate(client, _job(name, probe, genre, warm_w, warm_h,
                                          runner.draft_steps(genre.steps), "invoke-image-benchmark",
                                          out_dir, True), template, [1], version))
        width, height = sizing.dimensions("1:1", entry["family"])
        try:
            [result] = list(runner.generate(client, _job(name, probe, genre, width, height, genre.steps,
                                                         "invoke-image-benchmark", out_dir, False),
                                            template, [1234], version))
            seconds = result["seconds"]
        except InvokeError as exc:
            print(f"{name}: {exc}", file=sys.stderr)
            seconds = None
        entry["seconds_1024"] = seconds
        print(json.dumps({"model": name, "seconds_1024": seconds, "verdict": gate_verdict(seconds)}), flush=True)
    (skill / "models.json").write_text(json.dumps(registry, indent=2) + "\n")
    return 0
```

In `build_parser`, before `return parser`:

```python
    selftest = sub.add_parser("selftest")
    selftest.add_argument("--accept-version", action="store_true")
    selftest.set_defaults(func=cmd_selftest)

    bench = sub.add_parser("benchmark")
    bench.add_argument("--model")
    bench.add_argument("--accept-version", action="store_true")
    bench.set_defaults(func=cmd_benchmark)
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests -q`
Expected: PASS

- [ ] **Step 3: Run selftest against the live server**

Run: `cd skills/invoke-image && ./scripts/invoke.py selftest`
Expected: two JSON lines (`flux`, `sdxl`), both `"ok": true`, exit 0. Read both PNGs with the Read tool and confirm each shows an apple. If a family fails, fix its template (Task 8) before continuing.

- [ ] **Step 4: Run the benchmark**

Run: `cd skills/invoke-image && ./scripts/invoke.py benchmark`
Expected: one line per model with `seconds_1024` and a verdict; `models.json` updated. Report the numbers to the user. Any `SLOW` model must not be a genre default in Task 10 (it may stay in `allowed_models`). If `flux-dev` is SLOW and a smaller GGUF exists, ask the user whether to install it and rerun `benchmark --model flux-dev`.

- [ ] **Step 5: Commit**

```bash
git add skills/invoke-image/scripts/invoke.py skills/invoke-image/tests/test_cli.py skills/invoke-image/models.json
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add selftest and benchmark with speed gate"
```

---

### Task 10: Starter genres and `sync-presets`

**Files:**
- Create: `skills/invoke-image/genres/{photographic,editorial-food,interior-architectural,flat-vector,line-icon,watercolor,isometric-3d,seamless-texture}.json`
- Modify: `skills/invoke-image/scripts/invoke.py` (add `sync-presets`)
- Test: `skills/invoke-image/tests/test_genres.py`

**Interfaces:**
- Consumes: `styles.load_genre`, `styles.preset_positive`, `Client.list_presets`, `Client.create_preset`, `Client.update_preset`.
- Produces: 8 genre files; preset names `invoke-image <genre>` in InvokeAI.

- [ ] **Step 1: Write the failing test**

`tests/test_genres.py`:

```python
import json
from pathlib import Path

import pytest

from invoke_image import graph, styles

SKILL = Path(__file__).resolve().parents[1]
STARTERS = ["photographic", "editorial-food", "interior-architectural", "flat-vector",
            "line-icon", "watercolor", "isometric-3d", "seamless-texture"]
REGISTRY = json.loads((SKILL / "models.json").read_text())


@pytest.mark.parametrize("name", STARTERS)
def test_starter_genre_valid(name):
    genre = styles.load_genre(SKILL / "genres", name)
    assert genre.name == name
    for model in genre.allowed_models:
        assert model in REGISTRY["models"], model
    default = REGISTRY["models"][genre.model]
    seconds = default["seconds_1024"]
    assert seconds is not None and seconds <= 300, f"{genre.model} failed the speed gate"
    template = default["template"] + genre.template_suffix
    graph.load_template(SKILL / "graphs", template)


def test_vector_genres_vectorize():
    assert styles.load_genre(SKILL / "genres", "flat-vector").vectorize
    assert styles.load_genre(SKILL / "genres", "line-icon").vectorize


def test_seamless_uses_seamless_template():
    assert styles.load_genre(SKILL / "genres", "seamless-texture").template_suffix == "-seamless"
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_genres.py -q`
Expected: FAIL with `StyleError: unknown genre 'photographic'`

- [ ] **Step 2: Write the genre files**

Defaults below assume Task 9 passed for `juggernaut-xl` and `sdxl-base` and that `juggernaut-xl` is `commercial_ok`. If Juggernaut is SLOW or not commercial, set `"model": "sdxl-base"` in the three photo genres. If `flux-dev` is SLOW, leave it in `allowed_models` only.

`genres/photographic.json`:

```json
{
  "name": "photographic",
  "model": "juggernaut-xl",
  "allowed_models": ["juggernaut-xl", "sdxl-base", "flux-dev"],
  "positive": "{subject}, professional photograph, natural light, 35mm lens, shallow depth of field, true-to-life color, {brand}",
  "negative": "illustration, painting, cartoon, 3d render, oversaturated, plastic skin, deformed hands, extra fingers, text, watermark, logo, blurry, lowres",
  "steps": 30,
  "cfg": 5.0
}
```

`genres/editorial-food.json`:

```json
{
  "name": "editorial-food",
  "model": "juggernaut-xl",
  "allowed_models": ["juggernaut-xl", "sdxl-base", "flux-dev"],
  "positive": "{subject}, editorial food photography, appetizing, soft window light, 50mm lens, shallow depth of field, styled table setting, magazine quality, {brand}",
  "negative": "illustration, cartoon, 3d render, plastic-looking food, unappetizing, oversaturated, deformed cutlery, text, watermark, logo, blurry, lowres",
  "steps": 30,
  "cfg": 5.0
}
```

`genres/interior-architectural.json`:

```json
{
  "name": "interior-architectural",
  "model": "juggernaut-xl",
  "allowed_models": ["juggernaut-xl", "sdxl-base", "flux-dev"],
  "positive": "{subject}, architectural interior photography, wide angle 24mm lens, straight verticals, balanced natural and ambient light, clean composition, {brand}",
  "negative": "fisheye distortion, tilted verticals, cluttered, people in focus, illustration, cartoon, text, watermark, logo, blurry, lowres",
  "steps": 30,
  "cfg": 5.0
}
```

`genres/flat-vector.json`:

```json
{
  "name": "flat-vector",
  "model": "sdxl-base",
  "allowed_models": ["sdxl-base", "flux-dev"],
  "positive": "{subject}, flat vector illustration, clean geometric shapes, solid fills, limited color palette, no gradients, crisp edges, plain background, {brand}",
  "negative": "photo, photorealistic, 3d render, gradient, texture, noise, shading, text, watermark, signature, blurry",
  "steps": 30,
  "cfg": 6.0,
  "vectorize": true
}
```

`genres/line-icon.json`:

```json
{
  "name": "line-icon",
  "model": "sdxl-base",
  "allowed_models": ["sdxl-base", "flux-dev"],
  "positive": "{subject}, simple line icon, single consistent stroke weight, monoline, minimal, centered, dark lines on a white background, {brand}",
  "negative": "photo, 3d, shading, gradient, solid fill, texture, multiple icons, text, letters, watermark, blurry",
  "steps": 30,
  "cfg": 6.5,
  "vectorize": true
}
```

`genres/watercolor.json`:

```json
{
  "name": "watercolor",
  "model": "sdxl-base",
  "allowed_models": ["sdxl-base", "flux-dev"],
  "positive": "{subject}, loose watercolor illustration, visible paper texture, soft bleeding edges, transparent washes, hand-painted, {brand}",
  "negative": "photo, photorealistic, 3d render, digital airbrush, hard outlines, text, watermark, signature, blurry, lowres",
  "steps": 30,
  "cfg": 6.0
}
```

`genres/isometric-3d.json`:

```json
{
  "name": "isometric-3d",
  "model": "sdxl-base",
  "allowed_models": ["sdxl-base", "flux-dev"],
  "positive": "{subject}, isometric 3d illustration, soft studio lighting, clean matte materials, 30 degree isometric angle, simple pastel background, {brand}",
  "negative": "photo, perspective distortion, fisheye, cluttered, noisy textures, text, watermark, blurry, lowres",
  "steps": 30,
  "cfg": 6.0
}
```

`genres/seamless-texture.json`:

```json
{
  "name": "seamless-texture",
  "model": "sdxl-base",
  "allowed_models": ["sdxl-base"],
  "positive": "{subject}, seamless tileable texture, evenly distributed pattern, flat lighting, top-down view, no focal point, {brand}",
  "negative": "vignette, border, frame, focal object, perspective, cast shadows, text, watermark, blurry",
  "steps": 30,
  "cfg": 6.0,
  "template_suffix": "-seamless"
}
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests -q`
Expected: PASS

- [ ] **Step 3: Add `sync-presets`**

In `scripts/invoke.py`, add after `cmd_benchmark`:

```python
def cmd_sync_presets(args):
    skill = Path(args.skill_dir)
    registry = load_registry(skill)
    client, _ = connect(registry, args.accept_version)
    existing = {preset["name"]: preset for preset in client.list_presets()}
    for path in sorted((skill / "genres").glob("*.json")):
        genre = styles.load_genre(skill / "genres", path.stem)
        name = f"invoke-image {genre.name}"
        positive = styles.preset_positive(genre)
        if name in existing:
            client.update_preset(existing[name]["id"], name, positive, genre.negative)
            print(f"updated: {name}")
        else:
            client.create_preset(name, positive, genre.negative)
            print(f"created: {name}")
    return 0
```

In `build_parser`, before `return parser`:

```python
    sync = sub.add_parser("sync-presets")
    sync.add_argument("--accept-version", action="store_true")
    sync.set_defaults(func=cmd_sync_presets)
```

- [ ] **Step 4: Verify against the live server**

Run: `cd skills/invoke-image && ./scripts/invoke.py sync-presets && ./scripts/invoke.py sync-presets`
Expected: first run prints 8 `created:` lines, second prints 8 `updated:` lines. In the UI Style Presets list, `invoke-image photographic` shows positive `{prompt}, professional photograph, ...`. If the create call returns HTTP 422, read the error body, adjust `Client._preset_fields` to the fields it names, add the failing field to `test_create_preset_multipart`, and rerun.

- [ ] **Step 5: One live render per genre**

```bash
cd /tmp/ii-check
for g in photographic editorial-food interior-architectural flat-vector line-icon watercolor isometric-3d seamless-texture; do
  ~/summit-claude-skills-invoke-image/skills/invoke-image/scripts/invoke.py gen --genre $g --subject "a coffee cup" --n 1 --draft || break
done
montage -label '%t' generated/*-draft.png -tile 4x -geometry 384x384+6+6 generated/sheet.png
magick generated/*seamless-texture*-draft.png -roll +50%+50% generated/seam-check.png
```

Expected: 8 drafts and a contact sheet. Read `sheet.png`: each tile reads as its genre. Read `seam-check.png`: no visible seam cross through the middle.

- [ ] **Step 6: Commit**

```bash
git add skills/invoke-image/genres skills/invoke-image/scripts/invoke.py skills/invoke-image/tests/test_genres.py
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add 8 starter genres and style preset sync"
```

---

### Task 11: Upscale and vectorize

**Files:**
- Create: `skills/invoke-image/scripts/invoke_image/vector.py`
- Modify: `skills/invoke-image/scripts/invoke.py` (add `upscale`, `vectorize`; `gen --no-vectorize`; auto-vectorize finals)
- Test: `skills/invoke-image/tests/test_vector.py`

**Interfaces:**
- Consumes: `Client.model`, `Client.board_id`, `Client.enqueue`, `Client.wait`, `Client.download`, `runner.final_image`, `runner.timeout_for`, `graph.load_template`, `graph.fill`, `output.write_sidecar`, `styles.find_brand`, `styles.check_license`.
- Produces: `vector.posterize(src, dst, colors=6)`, `vector.trace(png, svg)`, `vector.rasterize(svg, png, width=1024)`, `vector.vectorize(png: Path, colors=6) -> tuple[Path, Path]` returning `(svg, svgcheck_png)`; CLI `upscale --image PNG`, `vectorize --image PNG`, `gen --no-vectorize`.

- [ ] **Step 1: Write the failing test**

`tests/test_vector.py`:

```python
import subprocess

from invoke_image import vector


def test_vectorize_round_trip(tmp_path):
    png = tmp_path / "icon.png"
    subprocess.run(["magick", "-size", "128x128", "xc:white", "-fill", "#c0392b",
                    "-draw", "circle 64,64 64,20", str(png)], check=True)
    svg, check = vector.vectorize(png)
    assert svg == tmp_path / "icon.svg" and "<path" in svg.read_text()
    assert check == tmp_path / "icon-svgcheck.png" and check.stat().st_size > 0
    assert not (tmp_path / "icon-poster.png").exists()
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_vector.py -q`
Expected: FAIL with `ImportError: cannot import name 'vector'`

- [ ] **Step 2: Implement `vector.py`**

`scripts/invoke_image/vector.py`:

```python
"""Raster to SVG: posterize with ImageMagick, trace with vtracer, render back for inspection."""
import subprocess
from pathlib import Path


def posterize(src, dst, colors=6):
    subprocess.run(["magick", str(src), "+dither", "-colors", str(colors), str(dst)], check=True)


def trace(png, svg):
    import vtracer

    vtracer.convert_image_to_svg_py(str(png), str(svg), colormode="color", hierarchical="stacked",
                                    mode="spline", filter_speckle=4, color_precision=6)


def rasterize(svg, png, width=1024):
    subprocess.run(["magick", "-background", "white", str(svg), "-resize", f"{width}x", str(png)], check=True)


def vectorize(png, colors=6):
    png = Path(png)
    poster = png.with_name(f"{png.stem}-poster.png")
    svg = png.with_suffix(".svg")
    check = png.with_name(f"{png.stem}-svgcheck.png")
    posterize(png, poster, colors)
    try:
        trace(poster, svg)
    finally:
        poster.unlink(missing_ok=True)
    rasterize(svg, check)
    return svg, check
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_vector.py -q`
Expected: PASS. If `TypeError` names an unexpected vtracer keyword, check `python -c "import vtracer; help(vtracer.convert_image_to_svg_py)"` inside `uv run --with vtracer` and match its parameter names.

- [ ] **Step 3: Add `upscale`, `vectorize`, and auto-vectorize to the CLI**

In `scripts/invoke.py`, add `import uuid` to the imports and `vector` to `from invoke_image import graph, output, runner, sizing, styles, vector`. Add after `cmd_sync_presets`:

```python
def cmd_upscale(args):
    skill = Path(args.skill_dir)
    registry = load_registry(skill)
    src = Path(args.image).resolve()
    side = json.loads(src.with_suffix(".json").read_text())
    upscaler = registry["upscaler"]
    styles.check_license([("upscaler", upscaler)], styles.find_brand(src.parent))
    template = graph.load_template(skill / "graphs", "upscale")
    client, version = connect(registry, args.accept_version)
    filled = graph.fill(template, {
        "image": {"image_name": side["invoke_image_name"]},
        "model": client.model(upscaler["invoke_key"]),
        "board": {"board_id": client.board_id(side.get("client") or "invoke-image")},
    })
    filled["id"] = str(uuid.uuid4())
    item = client.wait(client.enqueue(filled)[0], runner.timeout_for(upscaler, side["width"], side["height"]))
    name = runner.final_image(client, item)
    dest = output.output_path(src.parent, src.stem, "up", f"{upscaler['factor']}x")
    client.download(name, dest)
    factor = upscaler["factor"]
    output.write_sidecar(dest, {**side, "upscaled_from": src.name, "upscaler": upscaler["invoke_key"],
                                "upscaler_license": upscaler["license"], "width": side["width"] * factor,
                                "height": side["height"] * factor, "invoke_image_name": name,
                                "invokeai_version": version})
    print(json.dumps({"path": str(dest)}))
    return 0


def cmd_vectorize(args):
    svg, check = vector.vectorize(Path(args.image))
    print(json.dumps({"svg": str(svg), "svg_check": str(check)}))
    return 0
```

In `cmd_gen`, replace the final loop:

```python
    for result in runner.generate(client, job, template, seeds, version):
        if genre.vectorize and not args.draft and not args.no_vectorize:
            svg, check = vector.vectorize(Path(result["path"]))
            result.update(svg=str(svg), svg_check=str(check))
        print(json.dumps(result), flush=True)
    return 0
```

In `build_parser`, add `gen.add_argument("--no-vectorize", action="store_true")` with the other `gen` arguments, and before `return parser`:

```python
    up = sub.add_parser("upscale")
    up.add_argument("--image", required=True)
    up.add_argument("--accept-version", action="store_true")
    up.set_defaults(func=cmd_upscale)

    vec = sub.add_parser("vectorize")
    vec.add_argument("--image", required=True)
    vec.set_defaults(func=cmd_vectorize)
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests -q`
Expected: PASS

- [ ] **Step 4: Verify live**

```bash
cd /tmp/ii-check
~/summit-claude-skills-invoke-image/skills/invoke-image/scripts/invoke.py gen --genre photographic --subject "a coffee cup on a diner counter" --aspect 16:9 --n 1 --seed 99
~/summit-claude-skills-invoke-image/skills/invoke-image/scripts/invoke.py upscale --image generated/a-coffee-cup-on-a-diner-counter-photographic-99.png
~/summit-claude-skills-invoke-image/skills/invoke-image/scripts/invoke.py gen --genre line-icon --subject "a coffee cup" --n 1 --seed 7
magick identify generated/*-up-2x.png
```

Expected: upscaled PNG at 2688x1536 (2x of 1344x768); the line-icon run prints `svg` and `svg_check`. Read the `-svgcheck.png` and confirm the trace is clean.

- [ ] **Step 5: Commit**

```bash
git add skills/invoke-image/scripts skills/invoke-image/tests/test_vector.py
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add upscale and SVG vectorize"
```

---

### Task 12: SKILL.md, symlink, README, PR

**Files:**
- Create: `skills/invoke-image/SKILL.md`
- Modify: `README.md` (Summit Custom Skills table row; install-prompt entry 16, renumber MENTOR SKILLS to 17 and MENTOR COUNCIL to 18)
- Modify: `install-prompts/ALL-PROMPTS.md` only if it contains the numbered custom-skill install block (as of 2026-10-14 it does not include WATCH-VIDEO or WEB-MOTION; if still absent, leave it and note the drift in the PR body)

- [ ] **Step 1: Write SKILL.md**

`skills/invoke-image/SKILL.md`:

````markdown
---
name: invoke-image
description: Generate polished, brand-consistent website imagery locally with InvokeAI at zero cost. Genre presets (photographic, editorial-food, interior-architectural, flat-vector, line-icon, watercolor, isometric-3d, seamless-texture) combine with a per-client brand file. Drafts, contact-sheet review, final render, 2x upscale, SVG vectorize. Activates on "generate images for", "hero image", "make icons for", "image set for the site", "invoke-image", or any website redesign that needs new imagery.
---

# invoke-image

Local image generation through InvokeAI on this Mac. No paid APIs.

CLI: `~/.claude/skills/invoke-image/scripts/invoke.py <command>` (runs via `uv run --script`).
Run it from inside the client repo so the brand file is found.

## Before generating

1. `invoke.py status`. If the server is down, `gen` starts it (up to 120s).
2. Look for `<repo>/.claude/image-brand.json`. If the repo is a client site and it is missing, draft one with the user:

```json
{
  "client": "Client Name",
  "brand": "palette and mood words, e.g. warm cream and diner red, retro, morning light",
  "avoid": ["readable text", "logos"],
  "default_genres": ["editorial-food", "flat-vector"],
  "output_dir": "assets/generated"
}
```

A brand file may not set model, LoRAs, or license.

## Workflow

1. **Brief.** Turn the user's short ask into a `--subject` per image (rules below). Pick genres from `default_genres` or the ask. Pick `--aspect`: hero `16:9` or `21:9`, cards `4:3` or `3:2`, portrait `9:16`, icons and textures `1:1`.
2. **Draft.** `invoke.py gen --genre <g> --subject "<s>" --aspect <a> --n 4 --draft`. Each line printed is `{path, seed, seconds, model, retry}`.
3. **Review.** `montage -label '%t' <draft pngs> -tile 2x -geometry 512x512+8+8 sheet.png`, read the sheet, drop misses (bad anatomy, leaked text, artifacts, off-brief), show the user the rest.
4. **Final.** Re-render the chosen seed: `invoke.py gen --genre <g> --subject "<same s>" --aspect <a> --seed <seed>` (no `--draft`). Same model, full steps, so the composition carries over.
5. **Upscale heroes.** `invoke.py upscale --image <final png>` writes `<name>-up-2x.png`.
6. **Vector.** `flat-vector` and `line-icon` finals auto-vectorize to `.svg` plus `-svgcheck.png`. Read the check image before handing over the SVG. `invoke.py vectorize --image <png>` does it on demand.

## Writing the subject

- SDXL models (`juggernaut-xl`, `sdxl-base`): comma-separated descriptive phrases, subject first, then setting, lighting, and lens. Example: `stack of buttermilk pancakes, melting butter, maple syrup pour, chrome diner counter, early morning`.
- FLUX models (`flux-dev`, `flux-schnell`): full natural sentences, composition described spatially. Example: `A tall stack of buttermilk pancakes sits on the left of a chrome diner counter while syrup pours from above; morning light comes from a window on the right.`
- Never put readable words in the subject; models garble text. Add text in HTML or the design tool.
- Do not repeat the genre's style words; the genre template adds them.

## Genres

`photographic`, `editorial-food`, `interior-architectural` (photo, default Juggernaut XL or SDXL base); `flat-vector`, `line-icon` (vectorized); `watercolor`; `isometric-3d`; `seamless-texture` (tileable). Use `--model` to pick another model from a genre's `allowed_models`. New genres are JSON files in `genres/`; run `invoke.py sync-presets` after adding one so it appears in the InvokeAI UI.

## Outputs

`<output_dir>/<slug>-<genre>-<seed>.png` plus a `.json` sidecar with prompt, model, seed, license, and `invoke_image_name`. Without a brand file, output goes to `./generated/`. Each client gets an InvokeAI gallery board named after `client`; use the InvokeAI canvas for hands-on inpainting fixes.

## Rules

- Never pass `--accept-version` without asking the user. A version mismatch means the graph templates may be stale.
- Never swap to a different model because one is missing or slow; report it.
- Never use a model, LoRA, or upscaler whose `commercial_ok` is not true for a client repo. The CLI refuses; do not work around it.
- Show the user drafts before spending time on finals.

## Exit codes and failures

| Code | Meaning | Action |
|---|---|---|
| 2 | Config or input error (unknown genre, bad aspect, license refusal, missing template) | Read the message; fix the input |
| 3 | InvokeAI version differs from the pinned version | Ask the user: recapture templates, or rerun with `--accept-version` |
| 4 | Server or queue error (not installed model, timeout, failed job) | Report the InvokeAI error text verbatim |

An out-of-memory job is retried once at 0.75x size; the `retry` field says so. Tell the user.

## Maintenance

- `invoke.py selftest`: one 512px render per model family.
- `invoke.py benchmark [--model NAME]`: times each model at 1024px and records `seconds_1024` in `models.json`. Models over 300s must not be genre defaults.
- Recapturing templates after an InvokeAI upgrade: generate once in the UI with sentinel values, save the `enqueue_batch` body to `graphs/raw/`, then `invoke.py capture` (see the implementation plan, Task 8, for exact values). Update `invokeai_version` in `models.json`.
````

- [ ] **Step 2: Link the skill into Claude**

```bash
ls -la ~/.claude/skills/invoke-image 2>/dev/null && echo "EXISTS: stop and ask"
ln -s ~/summit-claude-skills-invoke-image/skills/invoke-image ~/.claude/skills/invoke-image
~/.claude/skills/invoke-image/scripts/invoke.py status
```

Expected: no pre-existing entry; `status` prints server state. After the PR merges and the main checkout is on `main`, repoint the link to `~/summit-claude-skills/skills/invoke-image` (tell the user; do not do it before the merge).

- [ ] **Step 3: Update the README**

In `README.md`, insert this row in the "Summit Custom Skills" table directly after the `web-motion` row:

```markdown
| **[invoke-image](skills/invoke-image/SKILL.md)** | Generates polished, brand-consistent website imagery locally through InvokeAI at zero cost. Genre presets plus a per-client brand file, draft and contact-sheet review, final render, 2x upscale, and SVG vectorize, with a license gate for client work. | "generate images for", "hero image", "make icons for" |
```

In the install-prompt block, insert after entry `15. WEB-MOTION`:

```markdown
16. INVOKE-IMAGE: When I need images for a website or say "generate images for", "hero image", or "make icons for", use the invoke-image skill to render locally through InvokeAI: read the client repo's brand file, draft four variants per image, show me a contact sheet, re-render my pick at full quality, upscale heroes, and vectorize icons. Never use a non-commercial model for client work and never swap models silently.
```

Renumber `16. MENTOR SKILLS` to `17.` and `17. MENTOR COUNCIL` to `18.` in place. Then check ALL-PROMPTS:

```bash
grep -n "WEB-MOTION\|WATCH-VIDEO" install-prompts/ALL-PROMPTS.md || echo "ALL-PROMPTS lacks the custom block: note drift in PR"
```

- [ ] **Step 4: Full verification**

```bash
cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests -q
cd ../.. && perl -ne 'print "$ARGV:$.\n" if /\xe2\x80\x94/; close ARGV if eof' $(git ls-files skills/invoke-image README.md docs/superpowers) | grep . || echo "no em dashes"
git diff --stat main...HEAD
```

Expected: all tests PASS; no em dashes; diff touches only `skills/invoke-image/`, `README.md`, and docs.

- [ ] **Step 5: Commit, push, open the PR (do not merge)**

```bash
git add skills/invoke-image/SKILL.md README.md
git commit -F <scratch>/msg.txt   # "docs(invoke-image): add SKILL.md and README entries"
git push -u origin feat/invoke-image
gh pr create --base docs/invoke-image-spec --head feat/invoke-image --title "feat: add invoke-image local image generation skill" --body-file <scratch>/pr.md
```

PR body (write with the Write tool): summary, benchmark numbers from Task 9, selftest result, the ALL-PROMPTS drift note if applicable, "Do not merge until Fly Trap acceptance (Task 13) passes", and the Claude Code attribution line. Base is `docs/invoke-image-spec` so the diff shows only implementation; retarget to `main` after PR #10 merges.

---

### Task 13: Fly Trap acceptance

Separate repository: `~/flytrap-website`. Work in a worktree; deliver via PR there; do not merge.

**Files (in `~/flytrap-website` worktree):**
- Create: `.claude/image-brand.json`
- Create: `assets/generated/*.png`, `*.json`, `*.svg` (only the finals the user picks)

- [ ] **Step 1: Prepare an isolated worktree**

```bash
cd ~/flytrap-website && git status --short && git log --oneline -5 && cat AGENTS.md | head -60
git fetch -q && git worktree add ../flytrap-website-imagery -b feat/generated-imagery-trial origin/main
cd ../flytrap-website-imagery && git check-ignore .claude/image-brand.json && echo "IGNORED: ask user before forcing"
```

Expected: worktree created on a new branch; `.claude/image-brand.json` not ignored. Follow any conventions AGENTS.md states.

- [ ] **Step 2: Draft the brand file from the site itself**

Read `colors_and_type.css`, the files in `assets/brand/`, and two or three photos in `assets/dishes/` to derive palette and mood words. Write `.claude/image-brand.json`, for example:

```json
{
  "client": "Fly Trap",
  "brand": "<palette and mood words derived from colors_and_type.css and the existing photos>",
  "avoid": ["readable text", "logos", "close-up faces", "brand names"],
  "default_genres": ["editorial-food", "interior-architectural", "flat-vector", "line-icon"],
  "output_dir": "assets/generated"
}
```

Show the brand line to the user and adjust before rendering.

- [ ] **Step 3: Draft four genres**

From the worktree root, with subjects written per the SKILL.md rules (ask the user for the 4 shots if they have preferences):
1. `editorial-food`, `16:9`: a signature dish hero
2. `interior-architectural`, `16:9`: the dining room
3. `flat-vector`, `1:1`: a spot illustration for a section divider
4. `line-icon`, `1:1`: three icons (hours, location, takeout), one run each

Each with `--n 4 --draft`. Build one contact sheet per genre with `montage` and show the user.

- [ ] **Step 4: Finals**

For each pick: re-render with `--seed <pick>`, upscale the two heroes, confirm the icon and spot SVG checks. Read every final at full size before showing it.

- [ ] **Step 5: Acceptance verdict**

Ask the user: "Polished enough to ship on the live Fly Trap site?" Record per-genre pass or fail.
- All pass: continue to Step 6.
- Any fail: tune that genre's prompt template in summit-claude-skills (`feat/invoke-image` branch, new commit), rerun Steps 3 and 4 for it. If prompt tuning cannot fix it and a style LoRA is the remedy, run Task 14.

- [ ] **Step 6: PR in flytrap-website (do not merge)**

```bash
git add .claude/image-brand.json assets/generated
git commit -F <scratch>/msg.txt   # "feat: add image brand file and trial generated imagery"
git push -u origin feat/generated-imagery-trial
gh pr create --title "feat: add image brand file and trial generated imagery" --body-file <scratch>/flytrap-pr.md
```

PR body: what each image is, genre, model, seed, license (from sidecars), that nothing is wired into pages yet, and the Claude Code attribution line. Then update the summit-claude-skills PR body with the acceptance result.

---

### Task 14 (conditional): Single-LoRA support

Run only if Task 13 Step 5 shows a genre needs a style LoRA.

**Files:**
- Modify: `skills/invoke-image/scripts/invoke_image/runner.py` (`build_values` adds LoRA values)
- Modify: `skills/invoke-image/models.json` (`loras` entry)
- Create: `skills/invoke-image/graphs/raw/sdxl-lora-batch.json`, `skills/invoke-image/graphs/sdxl-lora.json`
- Test: `skills/invoke-image/tests/test_runner.py` (append)

**Interfaces:**
- Produces: `build_values` adds `"lora": <model identifier dict>` and `"lora_weight": <float>` when `job.loras` has exactly one entry; raises `GraphError` for more than one. `runner.lora_ids(client, job) -> list[dict]` resolves identifiers via `client.model`.

- [ ] **Step 1: Pick and install a LoRA**

With the user, choose an SDXL LoRA whose license permits commercial use of outputs (OpenRAIL++-M, Apache-2.0, MIT, or CC-BY). Install it through the Model Manager. Add to `models.json`:

```json
"loras": {"<name>": {"invoke_key": "<key>", "source": "<source>", "license": "<license>", "commercial_ok": true}}
```

- [ ] **Step 2: Write the failing test**

Append to `tests/test_runner.py`:

```python
def test_build_values_single_lora(tmp_path):
    job = make_job(tmp_path, loras=[("ink", {"invoke_key": "k-ink"}, 0.7)])
    values = runner.build_values(job, 1, 1024, 1024, {"key": "k-sdxl"}, "b1", lora_ids=[{"key": "k-ink"}])
    assert values["lora"] == {"key": "k-ink"} and values["lora_weight"] == 0.7


def test_build_values_rejects_multiple_loras(tmp_path):
    from invoke_image.graph import GraphError
    job = make_job(tmp_path, loras=[("a", {}, 0.5), ("b", {}, 0.5)])
    with pytest.raises(GraphError, match="one LoRA"):
        runner.build_values(job, 1, 1024, 1024, {"key": "k"}, "b1", lora_ids=[{"key": "a"}, {"key": "b"}])
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_runner.py -q`
Expected: FAIL with `TypeError: build_values() got an unexpected keyword argument 'lora_ids'`

- [ ] **Step 3: Implement**

In `runner.py`, change `build_values` and thread `lora_ids` through `render` and `generate`:

```python
def build_values(job, seed, width, height, model_id, board_id, lora_ids=()):
    values = {
        "positive": job.prompt.positive,
        "negative": job.prompt.negative,
        "seed": seed,
        "width": width,
        "height": height,
        "steps": job.steps,
        "cfg": job.cfg,
        "model": model_id,
        "board": {"board_id": board_id},
    }
    if len(job.loras) > 1:
        raise graph.GraphError("templates support exactly one LoRA per genre")
    if job.loras:
        values["lora"] = lora_ids[0]
        values["lora_weight"] = job.loras[0][2]
    return values


def lora_ids(client, job):
    return [client.model(entry["invoke_key"]) for _, entry, _ in job.loras]
```

`render(client, template, job, seed, model_id, board_id, lora_ids=())` passes `lora_ids` to `build_values`. In `generate`, after `board_id = ...`, add `loras = lora_ids(client, job)` and pass `loras` to `render`. In `invoke.py` `cmd_gen` dry-run, pass `lora_ids=[{"key": e["invoke_key"]} for _, e, _ in loras]`.

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests -q`
Expected: PASS

- [ ] **Step 4: Teach `capture` the LoRA sentinels**

Append to `tests/test_cli.py`:

```python
def test_capture_lora_sentinels(tmp_path, capsys):
    skill = tmp_path / "skill"
    (skill / "graphs").mkdir(parents=True)
    raw = {"batch": {"graph": {"nodes": {
        "pos": {"prompt": "XPOSX"},
        "lora": {"lora": {"key": "lk", "name": "ink"}, "weight": 0.65}}}}}
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw))
    code = invoke.main(["--skill-dir", str(skill), "capture", "--raw", str(raw_path), "--name", "sdxl-lora",
                        "--positive", "XPOSX", "--lora-key", "lk", "--lora-weight", "0.65"])
    assert code == 0
    node = json.loads((skill / "graphs" / "sdxl-lora.json").read_text())["nodes"]["lora"]
    assert node == {"lora": "{{lora}}", "weight": "{{lora_weight}}"}
```

Run: `cd skills/invoke-image && uv run --python 3.13 --with pytest --with vtracer pytest tests/test_cli.py -q`
Expected: FAIL with `unrecognized arguments: --lora-key`

In `cmd_capture`, after the `image_name` block, add:

```python
    if args.lora_key:
        sentinels["lora"] = {"key": args.lora_key}
    if args.lora_weight is not None:
        sentinels["lora_weight"] = args.lora_weight
```

In `build_parser`, with the other `capture` arguments:

```python
    cap.add_argument("--lora-key")
    cap.add_argument("--lora-weight", type=float)
```

Run the tests again. Expected: PASS.

- [ ] **Step 4b: Capture the `sdxl-lora` template**

As Task 8 Step 3, with model SDXL base plus the chosen LoRA at weight `0.65`. Save the body to `graphs/raw/sdxl-lora-batch.json`, then:

```bash
./scripts/invoke.py capture --raw graphs/raw/sdxl-lora-batch.json --name sdxl-lora \
  --positive XPOSX --negative XNEGX --seed 424242 --width 1152 --height 896 \
  --steps 23 --cfg 5.5 --model-key <sdxl-base invoke_key> --board-id <capture board id> \
  --lora-key <lora invoke_key> --lora-weight 0.65
```

Expected: exit 0, every count at least 1.

- [ ] **Step 5: Use it and commit**

Add `"loras": [{"key": "<name>", "weight": 0.65}]` to the genre that needs it, rerun Task 13 Steps 3 to 5 for that genre, then:

```bash
git add skills/invoke-image
git commit -F <scratch>/msg.txt   # "feat(invoke-image): add single-LoRA template support"
git push
```
