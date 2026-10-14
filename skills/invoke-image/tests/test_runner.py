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
