# Wikipedia-API — CLI (Bash)

The `wikipedia-api` CLI is installed automatically with the package.

Full working example: [`examples/example_cli.sh`](../examples/example_cli.sh)

---

## Installation

```bash
pip install wikipedia-api
wikipedia-api --version
```

---

## Global Options

Every command accepts these options:

| Option                 | Description                                     | Default |
| ---------------------- | ----------------------------------------------- | ------- |
| `-l, --language`       | Wikipedia language edition                      | `en`    |
| `-u, --user-agent`     | HTTP User-Agent string                          | —       |
| `-v, --variant`        | Language variant (e.g. `zh-cn`, `zh-tw`)        | —       |
| `-f, --extract-format` | Extract format: `wiki` or `html`                | `wiki`  |
| `-n, --namespace`      | Wikipedia namespace number                      | `0`     |
| `--max-retries`        | Max retry attempts (0 to disable)               | `3`     |
| `--retry-wait`         | Base wait between retries (exponential backoff) | `1.0`   |
| `--json`               | Output as JSON                                  | —       |
| `-h, --help`           | Show help                                       | —       |

```bash
# Show all available commands
wikipedia-api --help

# Show help for a specific command
wikipedia-api summary --help
```

---

## Page Metadata

```bash
# Show page info (pageid, fullurl, editurl, length, lastrevid, etc.)
wikipedia-api page "Python (programming language)"

# JSON output — includes all info attributes
wikipedia-api page "Python (programming language)" --json

# Missing page — pageid will be -1 in JSON output
wikipedia-api page "Wikipedia-API-FooBar-DoesNotExist" --json
```

---

## Summary

```bash
wikipedia-api summary "Python (programming language)"

# Summary in Czech
wikipedia-api summary "Ostrava" --language cs

# Summary in Chinese with variant
wikipedia-api summary "Python" --language zh --variant zh-cn

# Summary as HTML
wikipedia-api summary "Ostrava" --language cs --extract-format html
```

---

## Full Text

```bash
wikipedia-api text "Python (programming language)"

# Full text as HTML
wikipedia-api text "Ostrava" --language cs --extract-format html
```

---

## Sections

```bash
# List the full section hierarchy
wikipedia-api sections "Python (programming language)"

wikipedia-api sections "Python (programming language)" --json

# Print the text of a specific section
wikipedia-api section "Python (programming language)" "Features and philosophy"
```

---

## Language Links

```bash
wikipedia-api langlinks "Python (programming language)"

wikipedia-api langlinks "Python (programming language)" --json
```

---

## Links and Backlinks

```bash
wikipedia-api links "Python (programming language)"

wikipedia-api links "Python (programming language)" --json

wikipedia-api backlinks "Python (programming language)"

wikipedia-api backlinks "Python (programming language)" --json
```

---

## Categories and Category Members

```bash
wikipedia-api categories "Python (programming language)"

wikipedia-api categories "Python (programming language)" --json

# List pages in a category
wikipedia-api categorymembers "Category:Physics"

# Recursively include subcategory members (depth 1)
wikipedia-api categorymembers "Category:Physics" --max-level 1

wikipedia-api categorymembers "Category:Physics" --json
```

---

## Language Variants

```bash
# Default script
wikipedia-api summary "Python" --language zh

# Simplified Chinese
wikipedia-api summary "Python" --language zh --variant zh-cn

# Traditional Chinese
wikipedia-api summary "Python" --language zh --variant zh-tw

# Singapore Simplified Chinese
wikipedia-api summary "Python" --language zh --variant zh-sg
```

---

## Coordinates

```bash
# Primary coordinate only (default)
wikipedia-api coordinates "London"

# All coordinates (primary + secondary)
wikipedia-api coordinates "London" --primary all

wikipedia-api coordinates "London" --json

wikipedia-api coordinates "Mount Everest"
```

---

## Images and Image Metadata

```bash
# List image titles used on a page
wikipedia-api images "Python (programming language)"

wikipedia-api images "Python (programming language)" --json

# Fetch metadata (URL, dimensions, MIME type, uploader, timestamp, etc.)
wikipedia-api images "Mount Everest" --imageinfo

wikipedia-api images "Mount Everest" --imageinfo --json

# Limit number of images
wikipedia-api images "Earth" --limit 20 --imageinfo
```

---

## Geosearch

```bash
# Search near a coordinate (London city centre)
wikipedia-api geosearch --coord "51.5074|-0.1278"

# Limit radius and result count
wikipedia-api geosearch --coord "51.5074|-0.1278" --radius 1000 --limit 5

# Search near a named page
wikipedia-api geosearch --page "Big Ben" --radius 1000

wikipedia-api geosearch --coord "48.8566|2.3522" --json
```

---

## Random Pages

```bash
wikipedia-api random

wikipedia-api random --limit 3

wikipedia-api random --limit 3 --json
```

---

## Search

```bash
wikipedia-api search "Python programming"

wikipedia-api search "Python programming" --limit 5

wikipedia-api search "Python programming" --json

# Search in another language
wikipedia-api search "машинное обучение" --language ru
```

---

## Retry Configuration

```bash
# Custom retry settings
wikipedia-api summary "Python (programming language)" --max-retries 5 --retry-wait 2.0

# Disable retries entirely (fail fast on first error)
wikipedia-api search "Python" --max-retries 0

# Aggressive retrying for unreliable connections
wikipedia-api geosearch --coord "27.9881|86.9250" --max-retries 10 --retry-wait 3.0
```

---

## Complete Workflow Example

```bash
UA="MyProject/1.0 (contact@example.com)"

# Explore a page from multiple angles
wikipedia-api summary "Python (programming language)" --user-agent "$UA"
wikipedia-api sections "Python (programming language)" --user-agent "$UA"
wikipedia-api section  "Python (programming language)" "History" --user-agent "$UA"
wikipedia-api categories "Python (programming language)" --user-agent "$UA"
wikipedia-api langlinks "Python (programming language)" --user-agent "$UA"

# Follow a language link to German Wikipedia
wikipedia-api summary "Python (Programmiersprache)" --language de --user-agent "$UA"

# Geographic pages
wikipedia-api coordinates "Mount Everest" --user-agent "$UA"
wikipedia-api geosearch --coord "27.9881|86.9250" --radius 5000 --user-agent "$UA"
wikipedia-api images "Mount Everest" --imageinfo --user-agent "$UA"

# Discovery
wikipedia-api random --limit 3 --user-agent "$UA"
wikipedia-api search "Mount Everest" --limit 5 --user-agent "$UA"
```
