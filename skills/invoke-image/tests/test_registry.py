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
    assert {"juggernaut-xl", "sdxl-base", "flux2-klein"} <= data["models"].keys()
    for name, entry in data["models"].items():
        assert REQUIRED <= entry.keys(), name
        assert entry["family"] in ("sdxl", "flux", "flux2"), name
        assert isinstance(entry["commercial_ok"], bool), name
    assert {"invoke_key", "source", "license", "commercial_ok", "factor"} <= data["upscaler"].keys()
