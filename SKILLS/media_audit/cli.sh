#!/usr/bin/env bash
# Skill: media_audit
# Goal: Audit all images used on a Wikipedia page via the CLI.
# Steps: list images → fetch imageinfo → display metadata summary

TOPIC="Mount Everest"
LANG="en"

# 1. List all images on the page
echo "=== Images on '$TOPIC' ==="
wikipedia-api images "$TOPIC" --language "$LANG"
echo

# 2. Fetch imageinfo (URL, dimensions, MIME, uploader) as text
echo "=== Image metadata ==="
wikipedia-api images "$TOPIC" --language "$LANG" --imageinfo
echo

# 3. Same as JSON for downstream processing (e.g. jq filtering)
echo "=== Image metadata (JSON) ==="
wikipedia-api images "$TOPIC" --language "$LANG" --imageinfo --json
echo
echo

# 4. Limit to first 5 images with metadata
echo "=== First 5 images with metadata ==="
wikipedia-api images "$TOPIC" --language "$LANG" --imageinfo --limit 5
