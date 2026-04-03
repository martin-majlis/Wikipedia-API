#!/usr/bin/env bash
# Skill: category_deep_dive
# Goal: Traverse a Wikipedia category tree using the CLI.
# Steps: list direct members → recurse one level into subcategories

CATEGORY="Category:Physics"
LANG="en"

# 1. Direct members (articles + subcategories, depth 0)
echo "=== Direct members of $CATEGORY ==="
wikipedia-api categorymembers "$CATEGORY" --language "$LANG"
echo

# 2. Members including one level of subcategory recursion
echo "=== Members (depth 1 — includes subcategory contents) ==="
wikipedia-api categorymembers "$CATEGORY" --max-level 1 --language "$LANG"
echo

# 3. JSON output for downstream processing
echo "=== Members JSON (depth 0) ==="
wikipedia-api categorymembers "$CATEGORY" --language "$LANG" --json | head -c 800
echo
echo

# 4. Inspect a specific subcategory directly
echo "=== Members of "Category:Physics by country ==="
wikipedia-api categorymembers ""Category:Physics by country" --language "$LANG"
