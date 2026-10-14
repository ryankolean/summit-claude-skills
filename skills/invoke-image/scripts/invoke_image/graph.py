"""InvokeAI node-graph templates: load, fill, capture helpers, result parsing."""
import copy
import json
import re
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


class GraphError(Exception):
    pass


def load_template(graphs_dir, name):
    path = Path(graphs_dir) / f"{name}.json"
    if not path.is_file():
        raise GraphError(f"graph template {name!r} not captured yet ({path}); see SKILL.md 'Recapturing templates'")
    return json.loads(path.read_text())


def placeholders(node):
    found = set()
    if isinstance(node, dict):
        for value in node.values():
            found |= placeholders(value)
    elif isinstance(node, list):
        for value in node:
            found |= placeholders(value)
    elif isinstance(node, str):
        found |= set(PLACEHOLDER.findall(node))
    return found


def fill(template, values):
    missing = placeholders(template) - set(values)
    if missing:
        raise GraphError(f"no value for placeholders: {', '.join(sorted(missing))}")
    return _fill(template, values)


def _fill(node, values):
    if isinstance(node, dict):
        return {key: _fill(value, values) for key, value in node.items()}
    if isinstance(node, list):
        return [_fill(value, values) for value in node]
    if isinstance(node, str):
        whole = PLACEHOLDER.fullmatch(node)
        if whole:
            return copy.deepcopy(values[whole.group(1)])
        return PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), node)
    return node


def collapse_batch_data(batch):
    result = copy.deepcopy(batch["graph"])
    for group in batch.get("data") or []:
        for datum in group:
            if datum["items"]:
                result["nodes"][datum["node_path"]][datum["field_name"]] = datum["items"][0]
    return result


def templatize(node, sentinels):
    counts = {name: 0 for name in sentinels}

    def walk(n):
        if isinstance(n, dict):
            for name, sentinel in sentinels.items():
                if isinstance(sentinel, dict) and all(n.get(k) == v for k, v in sentinel.items()):
                    counts[name] += 1
                    return "{{" + name + "}}"
            return {key: walk(value) for key, value in n.items()}
        if isinstance(n, list):
            return [walk(value) for value in n]
        if isinstance(n, str):
            for name, sentinel in sentinels.items():
                if isinstance(sentinel, str) and sentinel in n:
                    counts[name] += 1
                    n = n.replace(sentinel, "{{" + name + "}}")
            return n
        for name, sentinel in sentinels.items():
            if not isinstance(sentinel, (dict, str)) and type(n) is type(sentinel) and n == sentinel:
                counts[name] += 1
                return "{{" + name + "}}"
        return n

    return walk(copy.deepcopy(node)), counts


def output_image_names(queue_item):
    results = (queue_item.get("session") or {}).get("results") or {}
    names = []
    for out in results.values():
        if isinstance(out, dict) and out.get("type") == "image_output":
            name = (out.get("image") or {}).get("image_name")
            if name and name not in names:
                names.append(name)
    return names
