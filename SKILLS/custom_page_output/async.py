#!/usr/bin/env python3
# Skill: custom_page_output
# Goal: Build a single structured Markdown report for a Wikipedia page combining
#       text, images (with URLs), links, and categories (async version).
#
# All four content types are fetched concurrently with asyncio.gather for speed.

import asyncio
import sys

import wikipediaapi

USER_AGENT = "WikipediaAPI-Skills/1.0 (custom_page_output async)"
TOPIC = "Python (programming language)"
LANGUAGE = "en"


async def main() -> None:
    wiki = wikipediaapi.AsyncWikipedia(user_agent=USER_AGENT, language=LANGUAGE)
    page = wiki.page(TOPIC)

    if not await page.exists():
        print(f"Page '{TOPIC}' not found.", file=sys.stderr)
        return

    # Fetch all four content types concurrently
    summary, sections, images, links, categories = await asyncio.gather(
        page.summary,
        page.sections,
        page.images,
        page.links,
        page.categories,
    )

    # Batch imageinfo after images are fetched
    infos = await images.imageinfo()

    lines: list[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        f"# {page.title}",
        "",
        f"- **Page ID**: {await page.pageid}",
        f"- **Language**: {page.language}",
        f"- **URL**: {await page.fullurl}",
        "",
    ]

    # ── Summary ───────────────────────────────────────────────────────────────
    lines += ["## Summary", "", summary, ""]

    # ── Sections ──────────────────────────────────────────────────────────────
    lines.append("## Sections")
    lines.append("")
    for sec in sections:
        heading = "#" * (sec.level + 2)
        lines.append(f"{heading} {sec.title}")
        lines.append("")
        if sec.text.strip():
            lines.append(sec.text.strip())
            lines.append("")

    # ── Images ────────────────────────────────────────────────────────────────
    lines += ["## Images", ""]
    image_rows: list[str] = []
    for title, info_list in sorted(infos.items()):
        if not info_list or not info_list[0].url:
            continue
        info = info_list[0]
        dims = f"{info.width}x{info.height}" if info.width and info.height else "unknown"
        mime = info.mime or "unknown"
        image_rows.append(f"- [{title}]({info.url}) — {dims}, {mime}")

    lines += image_rows if image_rows else ["_(no images with accessible URLs)_"]
    lines.append("")

    # ── Links ─────────────────────────────────────────────────────────────────
    lines += ["## Links", "", f"_{len(links)} pages linked from this article_", ""]
    for title in sorted(links):
        lines.append(f"- {title}")
    lines.append("")

    # ── Categories ────────────────────────────────────────────────────────────
    lines += ["## Categories", ""]
    for title in sorted(categories):
        lines.append(f"- {title}")
    lines.append("")

    print("\n".join(lines))


asyncio.run(main())
