#!/usr/bin/env bash
# Skill: multilingual_content
# Goal: Read the same Wikipedia topic across multiple languages.
# Steps: English page info → langlinks → summary in target languages

TOPIC="Artificial intelligence"

# 1. English page info
echo "=== English page info ==="
wikipedia-api page "$TOPIC" --language en
echo

# 2. English summary
echo "=== English summary ==="
wikipedia-api summary "$TOPIC" --language en
echo

# 3. All language links (JSON for inspection)
echo "=== Language links ==="
wikipedia-api langlinks "$TOPIC" --language en
echo

# 4. German summary (title from langlinks: "Künstliche Intelligenz")
echo "=== German summary ==="
wikipedia-api summary "Künstliche Intelligenz" --language de
echo

# 5. French summary
echo "=== French summary ==="
wikipedia-api summary "Intelligence artificielle" --language fr
echo

# 6. Spanish summary
echo "=== Spanish summary ==="
wikipedia-api summary "Inteligencia artificial" --language es
