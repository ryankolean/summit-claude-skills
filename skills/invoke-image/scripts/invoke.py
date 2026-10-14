#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["vtracer"]
# ///
"""invoke-image CLI: drive a local InvokeAI to render brand-consistent images."""
import argparse
import json
import random
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from invoke_image import graph, output, runner, sizing, styles, vector  # noqa: E402
from invoke_image.client import Client, InvokeError  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parents[1]
LOG_PATH = Path.home() / ".cache" / "invoke-image" / "server.log"


class VersionMismatch(Exception):
    pass


def load_registry(skill_dir):
    return json.loads((Path(skill_dir) / "models.json").read_text())


def check_version(actual, registry, accept):
    pinned = registry.get("invokeai_version")
    if actual != pinned and not accept:
        raise VersionMismatch(
            f"InvokeAI is {actual} but graph templates were captured on {pinned}. "
            "Recapture the templates, or rerun with --accept-version after the user confirms."
        )


def connect(registry, accept_version):
    client = Client()
    version = client.ensure_running(registry["server"]["start"], LOG_PATH)
    check_version(version, registry, accept_version)
    return client, version


def cmd_status(args):
    registry = load_registry(args.skill_dir)
    client = Client()
    version = client.version()
    print(f"server: {'up ' + version if version else 'down'}")
    print(f"pinned version: {registry.get('invokeai_version')}")
    if not version:
        return 0
    for name, entry in sorted(registry["models"].items()):
        try:
            client.model(entry["invoke_key"])
            state = "installed"
        except InvokeError as exc:
            state = f"MISSING ({exc})"
        print(f"model {name}: {state}")
    return 0


def cmd_start(args):
    registry = load_registry(args.skill_dir)
    print(Client().ensure_running(registry["server"]["start"], LOG_PATH))
    return 0


def cmd_gen(args):
    skill = Path(args.skill_dir)
    registry = load_registry(skill)
    genre = styles.load_genre(skill / "genres", args.genre)
    brand = styles.find_brand(Path.cwd())
    model_name, entry = styles.resolve_model(genre, registry, args.model)
    loras = styles.resolve_loras(genre, registry)
    styles.check_license([(model_name, entry)] + [(key, lora) for key, lora, _ in loras], brand)
    prompt = styles.merge(genre, args.subject, brand)
    width, height = sizing.dimensions(args.aspect, entry["family"])
    job = runner.Job(
        genre=genre, prompt=prompt, subject=args.subject, model_name=model_name, model_entry=entry,
        width=width, height=height,
        steps=runner.draft_steps(genre.steps) if args.draft else genre.steps, cfg=genre.cfg,
        board=brand.client if brand else "invoke-image",
        out_dir=Path.cwd() if args.dry_run else output.resolve_output_dir(brand, Path.cwd()),
        draft=args.draft, loras=loras, brand_client=brand.client if brand else None,
    )
    template = graph.load_template(skill / "graphs", runner.template_name(job))
    seeds = args.seed or [random.randrange(2**31) for _ in range(args.n)]
    if args.dry_run:
        values = runner.build_values(job, seeds[0], width, height, {"key": entry["invoke_key"]}, "dry-run")
        print(json.dumps({
            "seeds": seeds, "positive": prompt.positive, "negative": prompt.negative,
            "width": width, "height": height, "steps": job.steps, "graph": graph.fill(template, values),
        }, indent=2))
        return 0
    client, version = connect(registry, args.accept_version)
    for result in runner.generate(client, job, template, seeds, version):
        if genre.vectorize and not args.draft and not args.no_vectorize:
            svg, check = vector.vectorize(Path(result["path"]))
            result.update(svg=str(svg), svg_check=str(check))
        print(json.dumps(result), flush=True)
    return 0


def cmd_capture(args):
    raw = json.loads(Path(args.raw).read_text())
    batch = raw.get("batch", raw)
    captured = graph.collapse_batch_data(batch)
    sentinels = {}
    for name in ("positive", "negative", "seed", "width", "height", "steps", "cfg"):
        value = getattr(args, name)
        if value is not None:
            sentinels[name] = value
    if args.model_key:
        sentinels["model"] = {"key": args.model_key}
    if args.board_id:
        sentinels["board"] = {"board_id": args.board_id}
    if args.image_name:
        sentinels["image"] = {"image_name": args.image_name}
    template, counts = graph.templatize(captured, sentinels)
    out = Path(args.skill_dir) / "graphs" / f"{args.name}.json"
    out.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"written": str(out), "replacements": counts}))
    unmatched = [name for name, count in counts.items() if count == 0]
    if unmatched:
        print(f"error: sentinel never matched: {', '.join(unmatched)}", file=sys.stderr)
        return 2
    return 0


GATE_SECONDS = 300
SELFTEST_SUBJECT = "a red apple on a white table, studio light"
CACHE_DIR = Path.home() / ".cache" / "invoke-image"


BLANK_STDDEV = 0.03


def is_blank(path):
    result = subprocess.run(["magick", str(path), "-colorspace", "Gray", "-format", "%[fx:standard_deviation]", "info:"],
                            capture_output=True, text=True, check=True)
    return float(result.stdout) < BLANK_STDDEV


def fresh_seed():
    # InvokeAI caches identical node outputs; a repeated seed returns instantly and fakes the timing.
    return random.randrange(2**31)


def adhoc_genre(name, model, steps, cfg):
    return styles.Genre(name=name, model=model, allowed_models=[model], positive="{subject}",
                        negative="blurry, watermark", steps=steps, cfg=cfg)


def gate_verdict(seconds):
    if seconds is None or seconds > GATE_SECONDS:
        return f"SLOW: over the {GATE_SECONDS}s gate; remove from genre defaults"
    return "ok"


def _job(name, entry, genre, width, height, steps, board, out_dir, draft):
    return runner.Job(genre=genre, prompt=styles.merge(genre, SELFTEST_SUBJECT), subject=SELFTEST_SUBJECT,
                      model_name=name, model_entry=entry, width=width, height=height, steps=steps,
                      cfg=genre.cfg, board=board, out_dir=out_dir, draft=draft)


def cmd_selftest(args):
    skill = Path(args.skill_dir)
    registry = load_registry(skill)
    client, version = connect(registry, args.accept_version)
    out_dir = CACHE_DIR / "selftest"
    out_dir.mkdir(parents=True, exist_ok=True)
    board = "invoke-image-selftest"
    failures, seen = 0, set()
    for name, entry in sorted(registry["models"].items()):
        if entry["family"] in seen:
            continue
        seen.add(entry["family"])
        genre = adhoc_genre("selftest", name, entry["benchmark_steps"], entry["benchmark_cfg"])
        width, height = sizing.dimensions("1:1", entry["family"], area=512 * 512)
        job = _job(name, entry, genre, width, height, runner.draft_steps(genre.steps), board, out_dir, True)
        template = graph.load_template(skill / "graphs", runner.template_name(job))
        [result] = list(runner.generate(client, job, template, [fresh_seed()], version))
        path = Path(result["path"])
        side = json.loads(path.with_suffix(".json").read_text())
        ok = (path.stat().st_size > 1000 and not is_blank(path)
              and side["invoke_image_name"] in client.board_image_names(client.board_id(board)))
        failures += not ok
        print(json.dumps({"family": entry["family"], "ok": ok, **result}), flush=True)
    return 1 if failures else 0


def cmd_benchmark(args):
    skill = Path(args.skill_dir)
    registry = load_registry(skill)
    client, version = connect(registry, args.accept_version)
    out_dir = CACHE_DIR / "benchmark"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, entry in sorted(registry["models"].items()):
        if args.model and name != args.model:
            continue
        genre = adhoc_genre("benchmark", name, entry["benchmark_steps"], entry["benchmark_cfg"])
        probe = dict(entry, seconds_1024=None)
        template = graph.load_template(skill / "graphs", entry["template"])
        warm_w, warm_h = sizing.dimensions("1:1", entry["family"], area=512 * 512)
        list(runner.generate(client, _job(name, probe, genre, warm_w, warm_h,
                                          runner.draft_steps(genre.steps), "invoke-image-benchmark",
                                          out_dir, True), template, [fresh_seed()], version))
        width, height = sizing.dimensions("1:1", entry["family"])
        try:
            [result] = list(runner.generate(client, _job(name, probe, genre, width, height, genre.steps,
                                                         "invoke-image-benchmark", out_dir, False),
                                            template, [fresh_seed()], version))
            seconds = result["seconds"]
        except InvokeError as exc:
            print(f"{name}: {exc}", file=sys.stderr)
            seconds = None
        entry["seconds_1024"] = seconds
        print(json.dumps({"model": name, "seconds_1024": seconds, "verdict": gate_verdict(seconds)}), flush=True)
    (skill / "models.json").write_text(json.dumps(registry, indent=2) + "\n")
    return 0


def cmd_upscale(args):
    skill = Path(args.skill_dir)
    registry = load_registry(skill)
    src = Path(args.image).resolve()
    side = json.loads(src.with_suffix(".json").read_text())
    upscaler = registry["upscaler"]
    styles.check_license([("upscaler", upscaler)], styles.find_brand(src.parent))
    template = graph.load_template(skill / "graphs", "upscale")
    client, version = connect(registry, args.accept_version)
    filled = graph.fill(template, {
        "image": {"image_name": side["invoke_image_name"]},
        "model": client.model(upscaler["invoke_key"]),
        "board": {"board_id": client.board_id(side.get("client") or "invoke-image")},
    })
    filled["id"] = str(uuid.uuid4())
    item = client.wait(client.enqueue(filled)[0], runner.timeout_for(upscaler, side["width"], side["height"]))
    name = runner.final_image(client, item)
    dest = output.output_path(src.parent, src.stem, "up", f"{upscaler['factor']}x")
    client.download(name, dest)
    factor = upscaler["factor"]
    output.write_sidecar(dest, {**side, "upscaled_from": src.name, "upscaler": upscaler["invoke_key"],
                                "upscaler_license": upscaler["license"], "width": side["width"] * factor,
                                "height": side["height"] * factor, "invoke_image_name": name,
                                "invokeai_version": version})
    print(json.dumps({"path": str(dest)}))
    return 0


def cmd_vectorize(args):
    svg, check = vector.vectorize(Path(args.image))
    print(json.dumps({"svg": str(svg), "svg_check": str(check)}))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="invoke.py")
    parser.add_argument("--skill-dir", default=str(SKILL_DIR))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("start").set_defaults(func=cmd_start)

    gen = sub.add_parser("gen")
    gen.add_argument("--genre", required=True)
    gen.add_argument("--subject", required=True)
    gen.add_argument("--aspect", default="1:1")
    gen.add_argument("--n", type=int, default=4)
    gen.add_argument("--seed", type=int, action="append")
    gen.add_argument("--model")
    gen.add_argument("--draft", action="store_true")
    gen.add_argument("--dry-run", action="store_true")
    gen.add_argument("--accept-version", action="store_true")
    gen.add_argument("--no-vectorize", action="store_true")
    gen.set_defaults(func=cmd_gen)

    cap = sub.add_parser("capture")
    cap.add_argument("--raw", required=True)
    cap.add_argument("--name", required=True)
    cap.add_argument("--positive")
    cap.add_argument("--negative")
    cap.add_argument("--seed", type=int)
    cap.add_argument("--width", type=int)
    cap.add_argument("--height", type=int)
    cap.add_argument("--steps", type=int)
    cap.add_argument("--cfg", type=float)
    cap.add_argument("--model-key")
    cap.add_argument("--board-id")
    cap.add_argument("--image-name")
    cap.set_defaults(func=cmd_capture)

    selftest = sub.add_parser("selftest")
    selftest.add_argument("--accept-version", action="store_true")
    selftest.set_defaults(func=cmd_selftest)

    bench = sub.add_parser("benchmark")
    bench.add_argument("--model")
    bench.add_argument("--accept-version", action="store_true")
    bench.set_defaults(func=cmd_benchmark)

    up = sub.add_parser("upscale")
    up.add_argument("--image", required=True)
    up.add_argument("--accept-version", action="store_true")
    up.set_defaults(func=cmd_upscale)

    vec = sub.add_parser("vectorize")
    vec.add_argument("--image", required=True)
    vec.set_defaults(func=cmd_vectorize)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (styles.StyleError, graph.GraphError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except VersionMismatch as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except InvokeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
