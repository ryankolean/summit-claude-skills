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
