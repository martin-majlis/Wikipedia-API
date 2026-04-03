#!/usr/bin/env python3
# Skill: media_audit
# Goal: Audit all images used on a Wikipedia page, filtering by file size.
# Steps: list images → batch imageinfo → display metadata → summarise findings

import wikipediaapi

USER_AGENT = "WikipediaAPI-Skills/1.0 (media_audit sync)"
TOPIC = "Mount Everest"
MIN_WIDTH = 500  # pixels — skip thumbnails smaller than this

wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="en")
page = wiki.page(TOPIC)

if not page.exists():
    print(f"Page '{TOPIC}' not found.")
    raise SystemExit(1)

print(f"=== Media audit: {page.title} ===\n")

# 1. List images on the page
images = page.images
print(f"Total images found: {len(images)}\n")

# 2. Batch-fetch imageinfo for all images at once (single API call)
infos = images.imageinfo()

# 3. Display metadata, filtering by minimum width
large_images = []
for title, info_list in sorted(infos.items()):
    if not info_list:
        continue
    info = info_list[0]
    width = info.width or 0
    height = info.height or 0
    if width >= MIN_WIDTH:
        large_images.append((title, info))
        print(f"  {title}")
        print(f"    URL:  {info.url}")
        print(f"    Size: {width}x{height}  MIME: {info.mime}")
        print(f"    User: {info.user}")
        print()

# 4. Summary
total = len([il for il in infos.values() if il])
print("--- Summary ---")
print(f"  Total images with metadata : {total}")
print(f"  Images >= {MIN_WIDTH}px wide: {len(large_images)}")
print(f"  Skipped (small/no info)    : {total - len(large_images)}")
