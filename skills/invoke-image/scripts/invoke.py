#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["vtracer"]
# ///
"""invoke-image CLI: drive a local InvokeAI to render brand-consistent images."""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from invoke_image import graph, output, runner, sizing, styles  # noqa: E402
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
        print(json.dumps(result), flush=True)
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
    gen.set_defaults(func=cmd_gen)
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
