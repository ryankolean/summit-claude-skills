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
