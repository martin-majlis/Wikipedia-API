---
name: category-deep-dive
description: Traverse a Wikipedia category tree, listing articles and subcategories
  at each level. Use when you want to explore the full scope of a topic area or build
  a hierarchical index of pages under a category.
argument-hint: [Category:Name] [max-depth]
---

# Category Deep Dive

## Overview

Fetch a Wikipedia category page and walk its member tree recursively:

1. **Category page** — verify it exists and report direct member counts
2. **Direct members** — list articles and subcategories at depth 0
3. **Recursion** — descend into each subcategory up to `MAX_LEVEL` deep

## When to use

- You want to enumerate all pages belonging to a broad topic
- You are building a dataset or index from a Wikipedia category tree
- You need to understand the sub-structure of a large category

## Parameters

| Parameter   | Description                                       | Default              |
| ----------- | ------------------------------------------------- | -------------------- |
| `CATEGORY`  | Full category title including `Category:` prefix  | `"Category:Physics"` |
| `MAX_LEVEL` | Maximum recursion depth (0 = direct members only) | `1`                  |
| `language`  | Wikipedia language edition                        | `en`                 |

## Examples

- Sync Python: [sync.py](sync.py)
- Async Python: [async.py](async.py)
- CLI: [cli.sh](cli.sh)

## Notes

- Category pages have namespace `14` (`Namespace.CATEGORY`); check `page.ns` to
  distinguish subcategories from articles when recursing.
- `categorymembers` is a lazy property — each subcategory you recurse into triggers
  a new API call.
- Large categories (e.g. `Category:Living people`) can have thousands of members;
  use `MAX_LEVEL = 0` and paginate carefully to avoid very long runs.
- CLI `--max-level` maps directly to the recursion depth parameter.
