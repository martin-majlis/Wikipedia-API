#!/usr/bin/env python3
# Skill: research_topic
# Goal: Deep-dive on a Wikipedia topic by chaining multiple API calls (async version).
# Steps: check existence → summary → sections → specific section → links → categories

import asyncio

import wikipediaapi

USER_AGENT = "WikipediaAPI-Skills/1.0 (research_topic async)"
TOPIC = "Python (programming language)"
SECTION = "History"


async def main():
    wiki = wikipediaapi.AsyncWikipedia(user_agent=USER_AGENT, language="en")
    page = wiki.page(TOPIC)

    # 1. Check existence
    if not await page.exists():
        print(f"Page '{TOPIC}' does not exist.")
        return

    print(f"=== {page.title} (pageid={await page.pageid}) ===\n")

    # 2. Summary
    print("--- Summary ---")
    print((await page.summary)[:500])
    print()

    # 3. Sections overview
    print("--- Sections ---")
    for sec in await page.sections:
        print(f"  {'  ' * (sec.level - 1)}[{sec.level}] {sec.title}")
    print()

    # 4. Read a specific section (section_by_title is sync — sections are already fetched above)
    print(f"--- Section: {SECTION} ---")
    section = page.section_by_title(SECTION)
    if section:
        print(section.text[:400])
    else:
        print(f"Section '{SECTION}' not found.")
    print()

    # 5. Links (first 10)
    links = await page.links
    print(f"--- Links ({len(links)} total, showing first 10) ---")
    for title in sorted(links)[:10]:
        print(f"  {title}")
    print()

    # 6. Categories
    categories = await page.categories
    print(f"--- Categories ({len(categories)} total) ---")
    for title in sorted(categories)[:10]:
        print(f"  {title}")


asyncio.run(main())
