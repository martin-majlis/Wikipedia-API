---
name: custom-page-output
description:
  Build a single structured report for a Wikipedia page combining text,
  images (with URLs), links, and categories. Use when you need a self-contained
  document with all key content from one page — for archiving, offline reading,
  reporting, or feeding into another tool.
argument-hint: [topic]
---

# Custom Page Output

## Overview

Fetch every major content type from one Wikipedia page and assemble them into a
single structured Markdown report:

1. **Page header** — title, page ID, URL, language
2. **Summary** — introductory text
3. **Sections** — full text of every top-level section with its heading
4. **Images** — list of files used on the page with their direct URLs and dimensions
5. **Links** — alphabetical list of all pages linked from this article
6. **Categories** — categories the page belongs to

## When to use

- You want a portable, self-contained snapshot of a Wikipedia article
- You need to feed structured article content into another tool or pipeline
- You want all images with their actual CDN URLs in one place
- You are archiving or caching Wikipedia content offline

## Output format

The output is a Markdown document with clearly delimited sections, suitable for
saving to a `.md` file or piping into another command.

## Parameters

| Parameter  | Description                | Default                           |
| ---------- | -------------------------- | --------------------------------- |
| `TOPIC`    | Wikipedia page title       | `"Python (programming language)"` |
| `language` | Wikipedia language edition | `en`                              |

## Examples

- Sync Python: [sync.py](sync.py)
- Async Python: [async.py](async.py)
- CLI: [cli.sh](cli.sh) — pipes individual commands into one report

## Notes

- Images are batch-fetched via `imageinfo()` — a single API call for all files.
- `info.url` may be `None` for files with restricted access; the report skips those.
- Links and categories are each lazy and trigger their own API call.
- The CLI version assembles the report by piping `--json` output from multiple
  commands and printing formatted sections in sequence.
