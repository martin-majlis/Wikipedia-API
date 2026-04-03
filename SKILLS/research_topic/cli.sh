#!/usr/bin/env bash
# Skill: research_topic
# Goal: Deep-dive on a Wikipedia topic by chaining multiple CLI commands.
# Steps: page info → summary → sections → specific section → links → categories

TOPIC="Python (programming language)"
SECTION="History"
LANG="en"

# 1. Page metadata (exists? pageid? url?)
echo "=== Page Info ==="
wikipedia-api page "$TOPIC" --language "$LANG"
echo

# 2. Summary
echo "=== Summary ==="
wikipedia-api summary "$TOPIC" --language "$LANG"
echo

# 3. Sections overview
echo "=== Sections ==="
wikipedia-api sections "$TOPIC" --language "$LANG"
echo

# 4. Read a specific section
echo "=== Section: $SECTION ==="
wikipedia-api section "$TOPIC" "$SECTION" --language "$LANG"
echo

# 5. Links (JSON so we can pipe/count if needed)
echo "=== Links (JSON) ==="
wikipedia-api links "$TOPIC" --language "$LANG" --json | head -c 500
echo
echo

# 6. Categories
echo "=== Categories ==="
wikipedia-api categories "$TOPIC" --language "$LANG"
