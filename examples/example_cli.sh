#!/usr/bin/env bash
# Comprehensive example of the Wikipedia-API CLI.
#
# Mirrors the structure of example_sync.py / example_async.py, covering
# every command available in the `wikipedia-api` tool.
#
# Run individual sections by copying commands directly to your terminal.

set -euo pipefail

USER_AGENT="Wikipedia-API Example (merlin@example.com)"

# ──────────────────────────────────────────────────────────────────────────────
# 1. Verify installation
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api --version

# ──────────────────────────────────────────────────────────────────────────────
# 2. Page metadata (equivalent to lazily fetched info attributes)
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api page "Python (programming language)" \
    --user-agent "$USER_AGENT"

# JSON output — includes pageid, fullurl, editurl, length, lastrevid, etc.
wikipedia-api page "Python (programming language)" \
    --user-agent "$USER_AGENT" --json

# ──────────────────────────────────────────────────────────────────────────────
# 3. Existence check — pageid is -1 for missing pages
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api page "Wikipedia-API-FooBar-DoesNotExist" \
    --user-agent "$USER_AGENT" --json

# ──────────────────────────────────────────────────────────────────────────────
# 4. Summary
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api summary "Python (programming language)" \
    --user-agent "$USER_AGENT"

# Summary in Czech
wikipedia-api summary "Ostrava" \
    --language cs --user-agent "$USER_AGENT"

# Summary in Chinese with variant
wikipedia-api summary "Python" \
    --language zh --variant zh-cn --user-agent "$USER_AGENT"

# ──────────────────────────────────────────────────────────────────────────────
# 5. Full text (summary + all sections)
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api text "Python (programming language)" \
    --user-agent "$USER_AGENT"

# Full text in HTML format
wikipedia-api text "Ostrava" \
    --language cs --extract-format html --user-agent "$USER_AGENT"

# ──────────────────────────────────────────────────────────────────────────────
# 6. Sections
# ──────────────────────────────────────────────────────────────────────────────

# List entire section hierarchy
wikipedia-api sections "Python (programming language)" \
    --user-agent "$USER_AGENT"

wikipedia-api sections "Python (programming language)" \
    --user-agent "$USER_AGENT" --json

# Print text of a specific section
wikipedia-api section "Python (programming language)" "Features and philosophy" \
    --user-agent "$USER_AGENT"

# ──────────────────────────────────────────────────────────────────────────────
# 7. Language links
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api langlinks "Python (programming language)" \
    --user-agent "$USER_AGENT"

wikipedia-api langlinks "Python (programming language)" \
    --user-agent "$USER_AGENT" --json

# ──────────────────────────────────────────────────────────────────────────────
# 8. Links and backlinks
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api links "Python (programming language)" \
    --user-agent "$USER_AGENT"

wikipedia-api links "Python (programming language)" \
    --user-agent "$USER_AGENT" --json

wikipedia-api backlinks "Python (programming language)" \
    --user-agent "$USER_AGENT"

wikipedia-api backlinks "Python (programming language)" \
    --user-agent "$USER_AGENT" --json

# ──────────────────────────────────────────────────────────────────────────────
# 9. Categories and category members
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api categories "Python (programming language)" \
    --user-agent "$USER_AGENT"

wikipedia-api categories "Python (programming language)" \
    --user-agent "$USER_AGENT" --json

# List pages in a category
wikipedia-api categorymembers "Category:Physics" \
    --user-agent "$USER_AGENT"

# Recursively list subcategory members (depth 1)
wikipedia-api categorymembers "Category:Physics" \
    --max-level 1 --user-agent "$USER_AGENT"

wikipedia-api categorymembers "Category:Physics" \
    --user-agent "$USER_AGENT" --json

# ──────────────────────────────────────────────────────────────────────────────
# 10. Language variants (Chinese)
# ──────────────────────────────────────────────────────────────────────────────

# Default script
wikipedia-api summary "Python" \
    --language zh --user-agent "$USER_AGENT"

# Simplified Chinese
wikipedia-api summary "Python" \
    --language zh --variant zh-cn --user-agent "$USER_AGENT"

# Traditional Chinese
wikipedia-api summary "Python" \
    --language zh --variant zh-tw --user-agent "$USER_AGENT"

# Singapore Simplified Chinese
wikipedia-api summary "Python" \
    --language zh --variant zh-sg --user-agent "$USER_AGENT"

# ──────────────────────────────────────────────────────────────────────────────
# 11. Coordinates
# ──────────────────────────────────────────────────────────────────────────────

# Primary coordinate only (default)
wikipedia-api coordinates "London" \
    --user-agent "$USER_AGENT"

# All coordinates (primary + secondary)
wikipedia-api coordinates "London" \
    --primary all --user-agent "$USER_AGENT"

wikipedia-api coordinates "London" \
    --user-agent "$USER_AGENT" --json

wikipedia-api coordinates "Mount Everest" \
    --user-agent "$USER_AGENT"

# ──────────────────────────────────────────────────────────────────────────────
# 12. Images and image metadata
# ──────────────────────────────────────────────────────────────────────────────

# List images used on a page
wikipedia-api images "Python (programming language)" \
    --user-agent "$USER_AGENT"

wikipedia-api images "Python (programming language)" \
    --user-agent "$USER_AGENT" --json

# Fetch image metadata (URL, dimensions, MIME type, uploader, timestamp, etc.)
wikipedia-api images "Mount Everest" \
    --imageinfo --user-agent "$USER_AGENT"

wikipedia-api images "Mount Everest" \
    --imageinfo --json --user-agent "$USER_AGENT"

# Limit number of images
wikipedia-api images "Earth" \
    --limit 20 --imageinfo --user-agent "$USER_AGENT"

# ──────────────────────────────────────────────────────────────────────────────
# 13. Geosearch
# ──────────────────────────────────────────────────────────────────────────────

# Search near a coordinate (London city centre)
wikipedia-api geosearch --coord "51.5074|-0.1278" \
    --user-agent "$USER_AGENT"

# Limit radius and number of results
wikipedia-api geosearch --coord "51.5074|-0.1278" \
    --radius 1000 --limit 5 --user-agent "$USER_AGENT"

# Search near a named page
wikipedia-api geosearch --page "Big Ben" \
    --radius 1000 --user-agent "$USER_AGENT"

wikipedia-api geosearch --coord "48.8566|2.3522" \
    --user-agent "$USER_AGENT" --json

# ──────────────────────────────────────────────────────────────────────────────
# 14. Random pages
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api random --user-agent "$USER_AGENT"

wikipedia-api random --limit 3 --user-agent "$USER_AGENT"

wikipedia-api random --limit 3 --user-agent "$USER_AGENT" --json

# ──────────────────────────────────────────────────────────────────────────────
# 15. Search
# ──────────────────────────────────────────────────────────────────────────────

wikipedia-api search "Python programming" \
    --user-agent "$USER_AGENT"

wikipedia-api search "Python programming" \
    --limit 5 --user-agent "$USER_AGENT"

wikipedia-api search "Python programming" \
    --user-agent "$USER_AGENT" --json

# Search in another language
wikipedia-api search "машинное обучение" \
    --language ru --user-agent "$USER_AGENT"

# ──────────────────────────────────────────────────────────────────────────────
# 16. Retry configuration
# ──────────────────────────────────────────────────────────────────────────────

# Custom retry settings
wikipedia-api summary "Python (programming language)" \
    --max-retries 5 --retry-wait 2.0 --user-agent "$USER_AGENT"

# Disable retries (fail fast)
wikipedia-api search "Python" \
    --max-retries 0 --user-agent "$USER_AGENT"

# Aggressive retrying for unreliable connections
wikipedia-api geosearch --coord "27.9881|86.9250" \
    --max-retries 10 --retry-wait 3.0 --user-agent "$USER_AGENT"
