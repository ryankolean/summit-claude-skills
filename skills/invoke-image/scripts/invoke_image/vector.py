"""Raster to SVG: posterize with ImageMagick, trace with vtracer, render back for inspection."""
import subprocess
from pathlib import Path


def posterize(src, dst, colors=6):
    subprocess.run(["magick", str(src), "+dither", "-colors", str(colors), str(dst)], check=True)


def trace(png, svg):
    import vtracer

    vtracer.convert_image_to_svg_py(str(png), str(svg), colormode="color", hierarchical="stacked",
                                    mode="spline", filter_speckle=4, color_precision=6)


def rasterize(svg, png, width=1024):
    subprocess.run(["magick", "-background", "white", str(svg), "-resize", f"{width}x", str(png)], check=True)


def vectorize(png, colors=6):
    png = Path(png)
    poster = png.with_name(f"{png.stem}-poster.png")
    svg = png.with_suffix(".svg")
    check = png.with_name(f"{png.stem}-svgcheck.png")
    posterize(png, poster, colors)
    try:
        trace(poster, svg)
    finally:
        poster.unlink(missing_ok=True)
    rasterize(svg, check)
    return svg, check
