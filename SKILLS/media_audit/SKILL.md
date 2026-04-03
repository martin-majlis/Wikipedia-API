---
name: media-audit
description: Audit all images used on a Wikipedia page. Use when you need to inventory
  media files, check image dimensions and MIME types, identify uploaders, or filter
  images by size for quality or licensing review.
argument-hint: [topic] [min-width-px]
---

# Media Audit

## Overview

Fetch all images from a Wikipedia page and retrieve their full metadata in one
batch request:

1. **Images list** — fetch all files used on the page (`prop=images`)
2. **Batch imageinfo** — retrieve URL, dimensions, MIME type, and uploader for
   every image in a single API call
3. **Filter** — keep only images above a minimum pixel width
4. **Summary** — report counts of large vs. small/missing images

## When to use

- You want to inventory all media on an article (for licensing or quality review)
- You need image URLs to download or re-host files
- You are filtering out small icons/thumbnails to find the main illustrations
- You want to know who uploaded images to a Wikipedia article

## Parameters

| Parameter   | Description                                        | Default           |
| ----------- | -------------------------------------------------- | ----------------- |
| `TOPIC`     | Wikipedia page title                               | `"Mount Everest"` |
| `MIN_WIDTH` | Minimum image width in pixels to include in report | `500`             |
| `language`  | Wikipedia language edition                         | `en`              |

## Examples

- Sync Python: [sync.py](sync.py)
- Async Python: [async.py](async.py)
- CLI: [cli.sh](cli.sh)

## Notes

- `images.imageinfo()` is a **batch** call — it fetches metadata for all images
  in one request, which is far more efficient than calling `imageinfo` per image.
- Images hosted on Wikimedia Commons return a `pageid` of `-1` with `known=""`
  in the raw API response; the library handles this transparently.
- `info.width` / `info.height` may be `None` for non-raster files (SVG, OGG, PDF).
- The async version awaits `images.imageinfo()` as a coroutine.
