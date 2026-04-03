---
name: explore-nearby
description: Discover Wikipedia pages near a geographic location. Use when you have
  a coordinate (lat/lon) and want to find what Wikipedia articles exist nearby, then
  read their summaries and coordinates.
argument-hint: [lat|lon] [radius-metres]
---

# Explore Nearby

## Overview

Find and explore Wikipedia pages close to a geographic point:

1. **Geosearch** — query pages within a given radius of a coordinate
2. **Summary** — fetch a short description of each nearby page
3. **Coordinates** — confirm the precise location of each result

## When to use

- You want to discover articles about places near a known location
- You are building a map or travel guide and need nearby POIs
- You have a coordinate from another source and want to contextualise it

## Parameters

| Parameter  | Description                                 | Default                    |
| ---------- | ------------------------------------------- | -------------------------- |
| `COORD`    | `GeoPoint(lat, lon)` or `"lat\|lon"` string | London: `51.5074\|-0.1278` |
| `RADIUS`   | Search radius in metres                     | `500`                      |
| `LIMIT`    | Maximum number of results                   | `5`                        |
| `language` | Wikipedia language edition                  | `en`                       |

## Examples

- Sync Python: [sync.py](sync.py)
- Async Python: [async.py](async.py)
- CLI: [cli.sh](cli.sh)

## Notes

- `page.geosearch_meta` is populated only on pages returned by `geosearch()`;
  it carries `dist`, `lat`, `lon`, and `primary` fields.
- The async version fetches all summaries and coordinates concurrently via the
  event loop — each `await page.summary` / `await page.coordinates` is independent.
- CLI: pass coordinates as `"lat|lon"` (pipe-separated, quoted).
