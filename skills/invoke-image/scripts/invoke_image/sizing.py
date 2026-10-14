"""Aspect ratio to pixel dimensions for each model family."""
import math

ASPECTS = {
    "1:1": 1.0,
    "4:3": 4 / 3,
    "3:4": 3 / 4,
    "16:9": 16 / 9,
    "9:16": 9 / 16,
    "3:2": 3 / 2,
    "2:3": 2 / 3,
    "21:9": 21 / 9,
}
MULTIPLE = {"sdxl": 64, "flux": 16, "flux2": 16}
DEFAULT_AREA = 1024 * 1024


def _round(value, multiple):
    return max(multiple, round(value / multiple) * multiple)


def _multiple(family):
    if family not in MULTIPLE:
        raise ValueError(f"unknown model family {family!r}; expected one of {', '.join(MULTIPLE)}")
    return MULTIPLE[family]


def dimensions(aspect, family, area=DEFAULT_AREA):
    if aspect not in ASPECTS:
        raise ValueError(f"unknown aspect {aspect!r}; use one of {', '.join(ASPECTS)}")
    multiple = _multiple(family)
    ratio = ASPECTS[aspect]
    width = math.sqrt(area * ratio)
    return _round(width, multiple), _round(width / ratio, multiple)


def scaled(width, height, factor, family):
    multiple = _multiple(family)
    return _round(width * factor, multiple), _round(height * factor, multiple)
