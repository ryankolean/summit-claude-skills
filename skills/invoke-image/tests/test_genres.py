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
