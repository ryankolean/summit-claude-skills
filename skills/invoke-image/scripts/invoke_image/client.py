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
