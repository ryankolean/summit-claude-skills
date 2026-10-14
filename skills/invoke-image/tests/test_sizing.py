import pytest

from invoke_image import sizing


@pytest.mark.parametrize(
    "aspect,family,expected",
    [
        ("1:1", "sdxl", (1024, 1024)),
        ("4:3", "sdxl", (1152, 896)),
        ("3:4", "sdxl", (896, 1152)),
        ("16:9", "sdxl", (1344, 768)),
        ("9:16", "sdxl", (768, 1344)),
        ("3:2", "sdxl", (1280, 832)),
        ("2:3", "sdxl", (832, 1280)),
        ("21:9", "sdxl", (1536, 640)),
        ("1:1", "flux", (1024, 1024)),
        ("4:3", "flux", (1184, 880)),
        ("16:9", "flux", (1360, 768)),
        ("9:16", "flux", (768, 1360)),
        ("3:2", "flux", (1248, 832)),
        ("21:9", "flux", (1568, 672)),
    ],
)
def test_dimensions(aspect, family, expected):
    assert sizing.dimensions(aspect, family) == expected


def test_dimensions_respect_family_multiple():
    for aspect in sizing.ASPECTS:
        w, h = sizing.dimensions(aspect, "sdxl")
        assert w % 64 == 0 and h % 64 == 0
        w, h = sizing.dimensions(aspect, "flux")
        assert w % 16 == 0 and h % 16 == 0


def test_small_area_for_selftest():
    assert sizing.dimensions("1:1", "sdxl", area=512 * 512) == (512, 512)


def test_unknown_aspect_lists_options():
    with pytest.raises(ValueError, match="16:9"):
        sizing.dimensions("5:4", "sdxl")


def test_unknown_family():
    with pytest.raises(ValueError, match="family"):
        sizing.dimensions("1:1", "sd15")


def test_scaled_for_oom_retry():
    assert sizing.scaled(1344, 768, 0.75, "sdxl") == (1024, 576)
    assert sizing.scaled(1360, 768, 0.75, "flux") == (1024, 576)
