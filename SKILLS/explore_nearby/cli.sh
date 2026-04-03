#!/usr/bin/env bash
# Skill: explore_nearby
# Goal: Discover Wikipedia pages near a geographic location.
# Steps: geosearch by coord → summary + coordinates for each result

# London, UK
COORD="51.5074|-0.1278"
RADIUS=500
LIMIT=5
LANG="en"

# 1. Geosearch — list nearby pages with distances
echo "=== Pages near $COORD (radius=${RADIUS}m) ==="
wikipedia-api geosearch --coord "$COORD" --radius "$RADIUS" --limit "$LIMIT" --language "$LANG"
echo

# 2. Get coordinates JSON for machine-readable output
echo "=== Geosearch results (JSON) ==="
wikipedia-api geosearch --coord "$COORD" --radius "$RADIUS" --limit "$LIMIT" \
    --language "$LANG" --json
echo

# 3. Fetch summary for the first known result (Big Ben is typically nearby)
echo "=== Summary: Big Ben ==="
wikipedia-api summary "Big Ben" --language "$LANG"
echo

# 4. Coordinates of that page
echo "=== Coordinates: Big Ben ==="
wikipedia-api coordinates "Big Ben" --language "$LANG"
