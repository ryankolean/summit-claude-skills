import subprocess

from invoke_image import vector


def test_vectorize_round_trip(tmp_path):
    png = tmp_path / "icon.png"
    subprocess.run(["magick", "-size", "128x128", "xc:white", "-fill", "#c0392b",
                    "-draw", "circle 64,64 64,20", str(png)], check=True)
    svg, check = vector.vectorize(png)
    assert svg == tmp_path / "icon.svg" and "<path" in svg.read_text()
    assert check == tmp_path / "icon-svgcheck.png" and check.stat().st_size > 0
    assert not (tmp_path / "icon-poster.png").exists()
