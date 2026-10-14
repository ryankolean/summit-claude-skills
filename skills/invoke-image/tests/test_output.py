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
