#!/usr/bin/env python3
# Skill: explore_nearby
# Goal: Discover Wikipedia pages near a geographic location (async version).
# Steps: geosearch by coord → fetch summary + coordinates for top results

import asyncio

import wikipediaapi
from wikipediaapi import GeoPoint

USER_AGENT = "WikipediaAPI-Skills/1.0 (explore_nearby async)"

# London, UK — 51.5074° N, 0.1278° W
COORD = GeoPoint(51.5074, -0.1278)
RADIUS = 500  # metres
LIMIT = 5


async def main():
    wiki = wikipediaapi.AsyncWikipedia(user_agent=USER_AGENT, language="en")

    # 1. Geosearch — find pages near the coordinate
    results = await wiki.geosearch(coord=COORD, radius=RADIUS, limit=LIMIT)
    print(f"=== Pages within {RADIUS}m of {COORD.lat},{COORD.lon} ===\n")

    for title, page in results.items():
        meta = page.geosearch_meta
        dist = f"{meta.dist:.0f}m" if meta else "?"
        print(f"--- {title} ({dist}) ---")

        # 2. Summary for each nearby page
        summary = await page.summary
        print(summary[:300] if summary else "(no summary)")
        print()

        # 3. Coordinates of the page itself
        coords = await page.coordinates
        if coords:
            c = coords[0]
            print(f"  Coordinates: lat={c.lat}, lon={c.lon}, globe={c.globe}")
        print()


asyncio.run(main())
