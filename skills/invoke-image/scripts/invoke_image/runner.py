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
