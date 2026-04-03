---
name: multilingual-content
description: Read the same Wikipedia topic across multiple languages. Use when you
  want to compare how a subject is described in different language editions, or when
  you need to find the correct foreign-language title for a page.
argument-hint: [topic] [lang1,lang2,...]
---

# Multilingual Content

## Overview

Fetch a Wikipedia article in English, then follow its language links to read the
same topic in other language editions:

1. **English page** — verify existence and read the English summary
2. **Language links** — retrieve all available translations
3. **Foreign summaries** — re-fetch the summary in each target language

## When to use

- You want to compare how different cultures describe the same topic
- You need the native-language title of a concept before fetching it directly
- You are building a multilingual knowledge base or translation tool

## Parameters

| Parameter      | Description                    | Default                     |
| -------------- | ------------------------------ | --------------------------- |
| `TOPIC`        | Wikipedia page title (English) | `"Artificial intelligence"` |
| `TARGET_LANGS` | List of BCP-47 language codes  | `["de", "fr", "ja", "es"]`  |

## Examples

- Sync Python: [sync.py](sync.py)
- Async Python: [async.py](async.py) — fetches all languages concurrently with `asyncio.gather`
- CLI: [cli.sh](cli.sh)

## Notes

- `page.langlinks` is a dict keyed by language code; each value is a page stub
  with the correct foreign title pre-set.
- You must create a new `Wikipedia(language=lang)` client to fetch content in a
  different language edition — the language is part of the base URL.
- Not every language link is guaranteed to have a summary; guard against empty strings.
- The async version uses `asyncio.gather` to fetch all target languages in parallel,
  making it significantly faster than sequential fetching.
