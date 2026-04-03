#!/usr/bin/env python3
# Skill: custom_page_output
# Goal: Build a single structured Markdown report for a Wikipedia page combining
#       text, images (with URLs), links, and categories.

import sys

import wikipediaapi

USER_AGENT = "WikipediaAPI-Skills/1.0 (custom_page_output sync)"
TOPIC = "Python (programming language)"
LANGUAGE = "en"

wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language=LANGUAGE)
page = wiki.page(TOPIC)

if not page.exists():
    print(f"Page '{TOPIC}' not found.", file=sys.stderr)
    raise SystemExit(1)

lines: list[str] = []

# ── Header ────────────────────────────────────────────────────────────────────
lines += [
    f"# {page.title}",
    "",
    f"- **Page ID**: {page.pageid}",
    f"- **Language**: {page.language}",
    f"- **URL**: {page.fullurl}",
    "",
]

# ── Summary ───────────────────────────────────────────────────────────────────
lines += ["## Summary", "", page.summary, ""]

# ── Sections ──────────────────────────────────────────────────────────────────
lines.append("## Sections")
lines.append("")
for sec in page.sections:
    heading = "#" * (sec.level + 2)  # h3 for level-1 sections
    lines.append(f"{heading} {sec.title}")
    lines.append("")
    if sec.text.strip():
        lines.append(sec.text.strip())
        lines.append("")

# ── Images ────────────────────────────────────────────────────────────────────
lines += ["## Images", ""]
images = page.images
infos = images.imageinfo()

image_rows: list[str] = []
for title, info_list in sorted(infos.items()):
    if not info_list or not info_list[0].url:
        continue
    info = info_list[0]
    dims = f"{info.width}x{info.height}" if info.width and info.height else "unknown"
    mime = info.mime or "unknown"
    image_rows.append(f"- [{title}]({info.url}) — {dims}, {mime}")

if image_rows:
    lines += image_rows
else:
    lines.append("_(no images with accessible URLs)_")
lines.append("")

# ── Links ─────────────────────────────────────────────────────────────────────
links = page.links
lines += ["## Links", "", f"_{len(links)} pages linked from this article_", ""]
for title in sorted(links):
    lines.append(f"- {title}")
lines.append("")

# ── Categories ────────────────────────────────────────────────────────────────
categories = page.categories
lines += ["## Categories", ""]
for title in sorted(categories):
    lines.append(f"- {title}")
lines.append("")

print("\n".join(lines))
