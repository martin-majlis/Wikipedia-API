---
name: research-topic
description: Deep-dive on a Wikipedia topic by chaining multiple API calls. Use when
  you need to fully explore a page: check existence, read summary, browse sections,
  read a specific section, list links to related pages, and list categories.
argument-hint: [topic] [section-title]
---

# Research Topic

## Overview

Fully explore a single Wikipedia page by chaining these steps in order:

1. **Check existence** — verify the page exists before fetching anything
2. **Summary** — read the introductory text
3. **Sections** — list the full section hierarchy
4. **Specific section** — read the body text of one named section
5. **Links** — list pages linked from this article
6. **Categories** — list the categories the page belongs to

## When to use

- You want a structured overview of a topic before going deeper
- You need to find related pages (via links or categories) to explore next
- You want to read one specific section without fetching the full text

## Parameters

| Parameter  | Description                     | Default                           |
| ---------- | ------------------------------- | --------------------------------- |
| `TOPIC`    | Wikipedia page title            | `"Python (programming language)"` |
| `SECTION`  | Section heading to read in full | `"History"`                       |
| `language` | Wikipedia language edition      | `en`                              |

## Examples

- Sync Python: [sync.py](sync.py)
- Async Python: [async.py](async.py)
- CLI: [cli.sh](cli.sh)

## Notes

- `section_by_title()` returns the _last_ section matching the heading; use
  `sections_by_title()` if the same heading appears multiple times.
- Links and categories are lazy — they trigger a separate API call each.
- In the async version, `section_by_title()` is synchronous (sections are already
  cached after `await page.sections`).
