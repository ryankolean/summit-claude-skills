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
