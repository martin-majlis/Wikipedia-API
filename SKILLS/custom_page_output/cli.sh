#!/usr/bin/env bash
# Skill: custom_page_output
# Goal: Build a single structured Markdown report for a Wikipedia page combining
#       text, images (with URLs), links, and categories — using only the CLI.

TOPIC="Python (programming language)"
LANG="en"

# ── Header ────────────────────────────────────────────────────────────────────
echo "# $TOPIC"
echo ""
wikipedia-api page "$TOPIC" --language "$LANG" --json \
    | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f'- **Page ID**: {d.get(\"pageid\", \"?\")}')
print(f'- **Language**: {d.get(\"language\", \"?\")}')
print(f'- **URL**: {d.get(\"url\", \"?\")}')
"
echo ""

# ── Summary ───────────────────────────────────────────────────────────────────
echo "## Summary"
echo ""
wikipedia-api summary "$TOPIC" --language "$LANG"
echo ""

# ── Sections ──────────────────────────────────────────────────────────────────
echo "## Sections"
echo ""
wikipedia-api sections "$TOPIC" --language "$LANG"
echo ""

# ── Images (with URLs via --imageinfo) ────────────────────────────────────────
echo "## Images"
echo ""
wikipedia-api images "$TOPIC" --language "$LANG" --imageinfo --json \
    | python3 -c "
import json, sys
data = json.load(sys.stdin)
for title, entries in sorted(data.items()):
    if not entries:
        continue
    info = entries[0]
    url = info.get('url') or ''
    w, h = info.get('width', '?'), info.get('height', '?')
    mime = info.get('mime', 'unknown')
    if url:
        print(f'- [{title}]({url}) — {w}x{h}, {mime}')
"
echo ""

# ── Links ─────────────────────────────────────────────────────────────────────
echo "## Links"
echo ""
wikipedia-api links "$TOPIC" --language "$LANG" --json \
    | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'_{len(data)} pages linked from this article_')
print()
for title in sorted(data):
    print(f'- {title}')
"
echo ""

# ── Categories ────────────────────────────────────────────────────────────────
echo "## Categories"
echo ""
wikipedia-api categories "$TOPIC" --language "$LANG"
