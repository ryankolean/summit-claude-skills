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
