---
name: cli-pandoc
description: >
  Teach Claude how to effectively use Pandoc for converting between document
  formats including Markdown, HTML, DOCX, PDF, EPUB, LaTeX, and dozens more.
  Activates when the user wants to convert documents, generate PDFs from
  Markdown, create slide decks, manage citations, or batch-convert between
  wiki/documentation formats.
---

# Pandoc — Universal Document Converter

**Repo:** https://github.com/jgm/pandoc

Convert between Markdown, HTML, DOCX, PDF, EPUB, LaTeX, reStructuredText,
and 40+ other formats. The definitive tool for document format conversion.

## When to Activate

**Manual triggers:**
- "Convert Markdown to PDF/DOCX/HTML"
- "Generate a PDF from my notes"
- "Create slides from Markdown"
- "Convert between document formats"
- "Add a table of contents to this doc"

**Auto-detect triggers:**
- User has a `.md` file and needs a different format for sharing
- User is writing documentation and needs it in multiple output formats
- User mentions citations, bibliographies, or academic writing
- User wants to convert wiki/Confluence/Notion exports to another format

## Key Commands

### Basic Conversion
```bash
pandoc input.md -o output.pdf          # Markdown to PDF (via LaTeX)
pandoc input.md -o output.docx         # Markdown to Word
pandoc input.md -o output.html         # Markdown to HTML
pandoc input.html -o output.md         # HTML to Markdown
pandoc input.docx -o output.md         # Word to Markdown (extract content)
pandoc input.md -o output.epub         # Markdown to EPUB
pandoc input.md -o output.tex          # Markdown to LaTeX source
```

### Specify Formats Explicitly (-f / -t)
```bash
pandoc -f markdown -t html input.md -o output.html
pandoc -f docx -t markdown input.docx -o output.md
pandoc -f rst -t markdown input.rst -o output.md
pandoc -f mediawiki -t markdown input.wiki -o output.md
pandoc -f org -t markdown input.org -o output.md
```

### List All Supported Formats
```bash
pandoc --list-input-formats   # All formats Pandoc can read
pandoc --list-output-formats  # All formats Pandoc can write
```

## HTML Output

```bash
# Standalone HTML (includes <html><head> tags)
pandoc input.md -o output.html --standalone

# With custom CSS
pandoc input.md -o output.html --standalone --css=style.css

# Embed CSS inline
pandoc input.md -o output.html --standalone \
  --variable=css:"body { font-family: sans-serif; max-width: 800px; margin: auto; }"

# Self-contained HTML (embeds images, CSS, JS)
pandoc input.md -o output.html --standalone --self-contained
```

## PDF Output

PDF generation requires a PDF engine. Pandoc supports several:

```bash
# Via LaTeX (best quality, requires TeX Live or MacTeX)
pandoc input.md -o output.pdf --pdf-engine=pdflatex
pandoc input.md -o output.pdf --pdf-engine=xelatex  # Unicode/font support
pandoc input.md -o output.pdf --pdf-engine=lualatex

# Via wkhtmltopdf (HTML-based, no LaTeX needed)
pandoc input.md -o output.pdf --pdf-engine=wkhtmltopdf

# Via weasyprint (CSS-based)
pandoc input.md -o output.pdf --pdf-engine=weasyprint
```

### PDF Page and Margin Settings
```bash
pandoc input.md -o output.pdf \
  -V geometry:margin=1in \
  -V geometry:papersize=letter \
  -V fontsize=12pt \
  -V mainfont="Georgia"
```

## DOCX Output

```bash
# Basic Word output
pandoc input.md -o output.docx

# Apply a reference document for styles
pandoc input.md -o output.docx --reference-doc=template.docx

# Generate a default reference doc to customize
pandoc --print-default-data-file reference.docx > template.docx
```

## Table of Contents

```bash
pandoc input.md -o output.pdf --toc                        # Add TOC
pandoc input.md -o output.pdf --toc --toc-depth=2          # TOC up to H2
pandoc input.md -o output.html --toc --standalone          # TOC in HTML
pandoc input.md -o output.docx --toc                       # TOC in Word
```

## Metadata

### Command-line Metadata
```bash
pandoc input.md -o output.pdf \
  --metadata title="My Document" \
  --metadata author="Jane Smith" \
  --metadata date="2024-03-28"
```

### YAML Metadata Block (in Markdown file)
```markdown
---
title: "My Document"
author: "Jane Smith"
date: "2024-03-28"
abstract: "This document covers..."
lang: "en"
---

# Introduction
...
```

### Metadata File
```bash
# Store metadata separately
pandoc input.md --metadata-file=meta.yaml -o output.pdf
```

## Templates

### Use a Custom Template
```bash
pandoc input.md -o output.pdf --template=mytemplate.tex
pandoc input.md -o output.html --template=mytemplate.html
```

### Print Default Template (to customize)
```bash
pandoc --print-default-template=latex > template.tex
pandoc --print-default-template=html5 > template.html
```

### Template Variables
```bash
pandoc input.md -o output.pdf \
  --variable=documentclass:article \
  --variable=classoption:twocolumn \
  --variable=fontfamily:palatino
```

## Slide Decks

### reveal.js (HTML slides)
```bash
pandoc input.md -o slides.html -t revealjs --standalone
pandoc input.md -o slides.html -t revealjs \
  --variable=theme:moon \
  --variable=transition:slide \
  --standalone

# Self-contained (embed reveal.js)
pandoc input.md -o slides.html -t revealjs --self-contained
```

### Beamer (PDF slides via LaTeX)
```bash
pandoc input.md -o slides.pdf -t beamer
pandoc input.md -o slides.pdf -t beamer \
  --variable=theme:metropolis \
  --variable=colortheme:crane
```

### Slide Structure in Markdown
```markdown
# Section Title (becomes a section divider)

## Slide Title

Content for this slide.

- Bullet one
- Bullet two

## Next Slide

---

(Horizontal rule creates a new slide without a title)
```

## Citations and Bibliographies

```bash
# Add citations (BibTeX, CSL JSON, etc.)
pandoc input.md -o output.pdf \
  --bibliography=references.bib \
  --csl=apa.csl \
  --citeproc

# Popular CSL styles (download from https://github.com/citation-style-language/styles)
# chicago-author-date.csl, ieee.csl, nature.csl, apa.csl

# Inline citation syntax in Markdown
# [@smith2024] — author-date
# [-@smith2024] — suppress author
# [@smith2024, p. 42] — page number
```

## Lua Filters

Filters let you transform the document AST programmatically.

```bash
pandoc input.md -o output.html --lua-filter=my-filter.lua
```

### Example Lua Filter (make all links open in new tab)
```lua
-- newwindow.lua
function Link(el)
  el.attributes.target = "_blank"
  return el
end
```

```bash
pandoc input.md -o output.html --lua-filter=newwindow.lua --standalone
```

## Advanced Patterns

### Batch Conversion with fd
```bash
# Convert all Markdown files in a project to HTML
fd -e md | while read f; do
  pandoc "$f" -o "${f%.md}.html" --standalone
done

# Markdown to PDF for all files in docs/
fd -e md . docs/ | while read f; do
  pandoc "$f" -o "pdf/$(basename ${f%.md}).pdf" --pdf-engine=xelatex
done
```

### Concatenate Multiple Files
```bash
# Single PDF from multiple Markdown files (ordered)
pandoc chapter1.md chapter2.md chapter3.md -o book.pdf --toc

# Combine all Markdown files in a directory
cat *.md | pandoc -f markdown -o combined.pdf
```

### Include Files (Markdown Extension)
```markdown
!include chapter1.md
!include chapter2.md
```
```bash
pandoc --lua-filter=include-files.lua input.md -o output.pdf
# (requires https://github.com/pandoc/lua-filters/tree/master/include-files)
```

### Convert Confluence / MediaWiki
```bash
# Confluence storage format to Markdown
pandoc -f html -t markdown confluence-export.html -o output.md

# MediaWiki to Markdown
pandoc -f mediawiki -t gfm input.wiki -o output.md  # GitHub-flavored Markdown

# Org-mode to Markdown
pandoc -f org -t markdown input.org -o output.md
```

### Professional PDF with Custom LaTeX Template
```bash
# Minimal LaTeX template variables for clean PDFs
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V mainfont="Palatino" \
  -V monofont="JetBrains Mono" \
  -V colorlinks=true \
  -V linkcolor=blue \
  --highlight-style=tango \
  --toc
```

### HTML to Clean Markdown (web scraping aid)
```bash
# Fetch a web page and convert to Markdown
curl -s https://example.com/article | pandoc -f html -t markdown -o article.md

# Remove extra blank lines
pandoc -f html -t markdown --wrap=none input.html -o output.md
```

## Supported Formats Reference

| Direction | Formats |
|---|---|
| Read (input) | Markdown (CommonMark, GFM, MMD, Pandoc), HTML, DOCX, ODT, LaTeX, EPUB, RST, Org, MediaWiki, Textile, JATS, OPML, CSV |
| Write (output) | All of above + PDF, reveal.js, Beamer, DokuWiki, Jira, ICML (InDesign), Jupyter, man page, PowerPoint (PPTX) |

## Markdown Flavor Options
```bash
pandoc -f commonmark     # CommonMark spec
pandoc -f gfm            # GitHub-Flavored Markdown
pandoc -f markdown       # Pandoc's extended Markdown (default, most features)
pandoc -f markdown-smart # Disable smart punctuation
```

## Chaining with Other Skills

- **cli-imagemagick:** Use ImageMagick to resize or optimize images before embedding them in Pandoc documents; convert PDF output pages to PNG with ImageMagick
- **fd:** Use `fd -e md` to find all Markdown files in a project, then pipe into a batch Pandoc conversion loop
- **cli-fzf (fzf):** Use `fd -e md | fzf` to interactively select a document before running `pandoc` on it
- **jq/yq:** Use `yq` to manipulate YAML metadata blocks before passing documents to Pandoc; use `jq` to work with Pandoc's JSON AST format (`pandoc -t json`)
