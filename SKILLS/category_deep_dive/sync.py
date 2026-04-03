#!/usr/bin/env python3
# Skill: category_deep_dive
# Goal: Traverse a Wikipedia category tree, listing members and recursing into subcategories.
# Steps: fetch category → list direct members → recurse one level into each subcategory

import wikipediaapi

USER_AGENT = "WikipediaAPI-Skills/1.0 (category_deep_dive sync)"
CATEGORY = "Category:Physics"
MAX_LEVEL = 1


def print_members(members: dict, level: int = 0, max_level: int = MAX_LEVEL) -> int:
    """Print category members recursively. Returns total count printed."""
    count = 0
    indent = "  " * level
    for title, page in members.items():
        ns_label = "Category" if page.ns == wikipediaapi.Namespace.CATEGORY else "Article"
        print(f"{indent}[{ns_label}] {title}")
        count += 1
        if page.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            sub = page.categorymembers
            count += print_members(sub, level + 1, max_level)
    return count


wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="en")
cat = wiki.page(CATEGORY)

if not cat.exists():
    print(f"Category '{CATEGORY}' not found.")
    raise SystemExit(1)

print(f"=== {cat.title} ===")
members = cat.categorymembers
articles = sum(1 for p in members.values() if p.ns != wikipediaapi.Namespace.CATEGORY)
subcats = sum(1 for p in members.values() if p.ns == wikipediaapi.Namespace.CATEGORY)
print(f"Direct members: {len(members)} ({articles} articles, {subcats} subcategories)\n")

total = print_members(members)
print(f"\nTotal entries shown (up to depth {MAX_LEVEL}): {total}")
