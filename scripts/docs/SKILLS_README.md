# SKILLS Verification

This directory contains example code samples demonstrating various Wikipedia-API capabilities. To verify that all code samples work correctly:

## Quick Start

```bash
# Run verification script
make verify-skills-sh

# Or run directly
./scripts/verify-skills.sh

# Or run Python script directly
uv run scripts/verify_skills.py
```

## What Gets Verified

The verification script runs all code samples in the SKILLS directory:

- **6 sync.py files** - Synchronous Wikipedia-API examples
- **6 async.py files** - Asynchronous Wikipedia-API examples
- **6 cli.sh files** - Command-line interface examples

## Current Status

As of the latest run:

- **Total scripts**: 18
- **Success rate**: 88.9% (16/18 passing)
- **Failed scripts**: 2
  - `category_deep_dive/cli.sh` - References non-existent category
  - `media_audit/cli.sh` - Times out due to large API response

## Script Categories

1. **category_deep_dive** - Explore Wikipedia category hierarchies
2. **custom_page_output** - Custom formatting of page content
3. **explore_nearby** - Geographic location exploration
4. **media_audit** - Image and media analysis
5. **multilingual_content** - Cross-language content comparison
6. **research_topic** - Topic research and analysis

## Troubleshooting

If scripts fail:

1. Check network connectivity to Wikipedia API
2. Verify the Wikipedia-API library is properly installed
3. Some scripts may timeout due to large API responses
4. CLI scripts require the `wikipedia-api` command to be available

## Manual Testing

To test individual scripts:

```bash
# Test a specific Python script
cd SKILLS/category_deep_dive
uv run sync.py

# Test a specific shell script
cd SKILLS/category_deep_dive
uv run bash cli.sh
```
