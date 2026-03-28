---
name: cli-imagemagick
description: >
  Teach Claude how to effectively use ImageMagick for image conversion,
  resizing, cropping, compositing, batch processing, and creating favicons,
  thumbnails, watermarks, and animated GIFs. Activates when the user wants
  to manipulate images, convert formats, batch-resize photos, or create
  image assets programmatically.
---

# ImageMagick — Image Manipulation Suite

**Repo:** https://github.com/ImageMagick/ImageMagick

Create, edit, compose, and convert images from the command line. Supports
200+ formats. The standard tool for programmatic image manipulation.

> **Note:** ImageMagick 7+ uses the `magick` command. Version 6 uses `convert`,
> `identify`, `mogrify`, etc. as separate commands. Examples use `magick`
> (v7) — replace with `convert`/`identify`/`mogrify` if on v6.

## When to Activate

**Manual triggers:**
- "Resize these images"
- "Convert images to PNG/JPEG/WebP"
- "Create a thumbnail"
- "Watermark images"
- "Create a favicon"
- "Make an animated GIF from frames"

**Auto-detect triggers:**
- User needs to batch-process a folder of images
- User needs image assets at specific dimensions for web/app
- User wants to add text or a logo overlay to images
- User extracted frames from FFmpeg and wants to process them

## Key Commands

### Inspect Images (magick identify)
```bash
magick identify image.png                        # Basic info (format, size, depth)
magick identify -verbose image.png              # Full metadata
magick identify -format "%wx%h\n" *.jpg         # Print dimensions for all JPEGs
magick identify -format "%f: %wx%h %[colorspace]\n" *.png  # Custom format
```

### Basic Conversion
```bash
magick input.png output.jpg                     # Convert format
magick input.jpg -quality 85 output.jpg         # Set JPEG quality (1-100)
magick input.png -quality 90 output.webp        # Convert to WebP
magick *.png output.pdf                         # Combine images into PDF
magick input.pdf output-%04d.png               # PDF pages to PNG sequence
```

### Resize (-resize)
```bash
magick input.jpg -resize 800x600 output.jpg     # Resize to fit within 800x600
magick input.jpg -resize 800x output.jpg        # Width 800, height proportional
magick input.jpg -resize x600 output.jpg        # Height 600, width proportional
magick input.jpg -resize 800x600! output.jpg    # Force exact size (distorts)
magick input.jpg -resize 800x600^ output.jpg    # Fill (crop to fit) 800x600
magick input.jpg -resize 50% output.jpg         # 50% of original size
magick input.jpg -resize 800x600> output.jpg    # Only shrink (don't enlarge)
magick input.jpg -resize 800x600< output.jpg    # Only enlarge (don't shrink)
```

### Crop (-crop)
```bash
magick input.jpg -crop 400x300+100+50 output.jpg  # width x height + x_offset + y_offset
magick input.jpg -gravity Center -crop 400x300+0+0 output.jpg  # Crop from center
magick input.jpg -trim output.jpg                  # Auto-trim whitespace/border
```

### Rotate, Flip, Flop
```bash
magick input.jpg -rotate 90 output.jpg          # Rotate 90° clockwise
magick input.jpg -rotate -45 output.jpg         # Rotate 45° counter-clockwise
magick input.jpg -flip output.jpg               # Vertical flip
magick input.jpg -flop output.jpg               # Horizontal flip
magick input.jpg -auto-orient output.jpg        # Fix EXIF orientation
```

### Color Adjustments
```bash
magick input.jpg -brightness-contrast 10x20 output.jpg     # Brightness +10, contrast +20
magick input.jpg -modulate 100,150,100 output.jpg           # Brightness,Saturation,Hue
magick input.jpg -colorspace Gray output.jpg                # Grayscale
magick input.jpg -negate output.jpg                         # Invert colors
magick input.jpg -level 20%,80% output.jpg                 # Levels (black/white point)
magick input.jpg -sigmoidal-contrast 3,50% output.jpg      # S-curve contrast
magick input.jpg -colorize 10,0,0 output.jpg               # Add red tint
```

### Blur and Sharpen
```bash
magick input.jpg -blur 0x2 output.jpg           # Gaussian blur, radius 0, sigma 2
magick input.jpg -sharpen 0x1 output.jpg        # Unsharp mask sharpen
magick input.jpg -unsharp 0x1+0.5+0.1 output.jpg  # Fine-tuned unsharp mask
magick input.jpg -median 3 output.jpg           # Median filter (noise reduction)
```

### Text Overlay (-annotate)
```bash
magick input.jpg \
  -font Arial -pointsize 48 -fill white -gravity South \
  -annotate +0+20 "Photo Caption" \
  output.jpg

# With stroke/outline
magick input.jpg \
  -font Arial -pointsize 48 \
  -fill white -stroke black -strokewidth 2 \
  -gravity Center -annotate +0+0 "Watermark" \
  output.jpg
```

### Border and Padding
```bash
magick input.jpg -border 10x10 -bordercolor white output.jpg  # White border
magick input.jpg -border 5% -bordercolor black output.jpg      # 5% border
magick input.jpg -gravity Center -extent 900x600 output.jpg    # Pad to exact canvas size
```

### Shadow and Effects
```bash
magick input.png -background none -shadow 50x5+4+4 \
  \( +clone -background none -shadow 50x5+4+4 \) \
  +swap -background white -layers merge output.png

magick input.jpg -vignette 0x20 output.jpg      # Vignette effect
magick input.jpg -charcoal 1 output.jpg         # Charcoal sketch effect
magick input.jpg -oil-paint 3 output.jpg        # Oil paint effect
```

### Transparency (-alpha)
```bash
magick input.png -alpha set -background none output.png         # Preserve transparency
magick input.jpg -transparent white output.png                  # Make white pixels transparent
magick input.png -fuzz 10% -transparent "#ffffff" output.png   # Fuzzy transparency
```

## Advanced Patterns

### Batch Processing with mogrify (in-place)
```bash
# Resize all JPEGs in a folder (modifies originals!)
magick mogrify -resize 1200x1200> *.jpg

# Convert all PNGs to JPEG (different extension = new files)
magick mogrify -format jpg *.png

# Resize and add watermark to all images, output to ./thumbs/
mkdir -p thumbs
magick mogrify -path thumbs -resize 300x300^ -gravity Center \
  -extent 300x300 -font Arial -pointsize 18 -fill "rgba(255,255,255,0.5)" \
  -gravity SouthEast -annotate +5+5 "© 2024" *.jpg
```

### Create Favicon (Multi-Size ICO)
```bash
# Generate all sizes from a source SVG or large PNG
magick source.png -resize 16x16 favicon-16.png
magick source.png -resize 32x32 favicon-32.png
magick source.png -resize 48x48 favicon-48.png
magick source.png -resize 64x64 favicon-64.png

# Combine into .ico
magick favicon-16.png favicon-32.png favicon-48.png favicon-64.png favicon.ico

# One-liner
magick source.png -define icon:auto-resize=64,48,32,16 favicon.ico
```

### Thumbnail Generation with Cropping
```bash
# Smart crop (crop-to-fill at exact size)
magick input.jpg -resize 300x300^ -gravity Center \
  -crop 300x300+0+0 +repage thumb.jpg

# Batch thumbnails preserving aspect ratio (letterbox)
magick input.jpg -thumbnail 300x300 -background white \
  -gravity Center -extent 300x300 thumb.jpg
```

### Watermarking
```bash
# Image watermark (logo overlay)
magick composite -gravity SouthEast -geometry +10+10 \
  logo.png input.jpg output.jpg

# Semi-transparent text watermark across entire image
magick input.jpg \
  \( -size 200x50 xc:none -font Arial -pointsize 24 \
     -fill "rgba(255,255,255,0.3)" -gravity Center \
     -annotate 0 "CONFIDENTIAL" \) \
  -gravity Center -composite output.jpg
```

### Image Comparison
```bash
magick compare input1.jpg input2.jpg diff.jpg         # Visual diff
magick compare -metric PSNR input1.jpg input2.jpg diff.jpg  # PSNR metric
magick compare -metric AE input1.jpg input2.jpg diff.jpg    # Absolute error pixels
```

### Create Animated GIF from Frames
```bash
# From image sequence (50ms delay = 20fps)
magick -delay 5 -loop 0 frame*.png animation.gif

# Control per-frame delay
magick \( frame1.png -delay 100 \) \( frame2.png -delay 50 \) \
  -loop 0 animation.gif

# Optimize GIF file size
magick -delay 5 -loop 0 frame*.png -layers optimize animation.gif
```

### Create Contact Sheet / Montage
```bash
# 4-column contact sheet with labels
magick montage *.jpg -geometry 200x200+5+5 -tile 4x montage.jpg

# Uniform grid, white background
magick montage *.png -background white -geometry 150x150+2+2 \
  -tile 5x -border 1 -bordercolor gray sheet.jpg
```

### Color Profile Conversion
```bash
magick input.jpg -profile /path/to/sRGB.icc -profile /path/to/CMYK.icc output.tif
magick input.jpg -colorspace sRGB output.jpg                # Convert to sRGB
magick input.jpg -strip output.jpg                          # Strip all metadata/profiles
```

### SVG to PNG Rendering
```bash
magick -background none input.svg output.png               # Transparent background
magick -background white -density 150 input.svg output.png # 150 DPI rasterization
magick -density 300 input.svg -resize 1000x output.png    # High-res render
```

### PDF to Images
```bash
# Requires Ghostscript
magick -density 150 input.pdf output-%04d.png    # All pages to PNG at 150 DPI
magick -density 150 "input.pdf[0]" cover.jpg    # First page only
```

### Sprites for Web
```bash
# Horizontal sprite strip
magick icon1.png icon2.png icon3.png +append sprite.png

# Vertical sprite strip
magick icon1.png icon2.png icon3.png -append sprite.png

# Grid sprite
magick montage icon*.png -geometry +0+0 -tile 4x sprite.png
```

## Chaining with Other Skills

- **cli-ffmpeg:** Extract video frames with FFmpeg (`-vf fps=1 frame_%04d.png`), then use ImageMagick's `mogrify` to batch-resize, watermark, or convert the frames
- **fd:** Use `fd -e jpg` to find all images recursively, pipe into a shell loop with `magick` for batch processing
- **cli-fzf (fzf):** Use `fd -e png | fzf` to interactively select an image before running a `magick` command
- **cli-pandoc:** Use ImageMagick to generate or preprocess images that are embedded in documents converted by Pandoc
