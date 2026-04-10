# Wikipedia-API

Python wrapper for the [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page).
Provides both synchronous (`Wikipedia`) and asynchronous (`AsyncWikipedia`) clients.

## Installation

```bash
pip install wikipedia-api
```

## Client Initialization

```python
import wikipediaapi

# Basic client — English Wikipedia, plain-text extract format
wiki = wikipediaapi.Wikipedia(
    user_agent="MyProject/1.0 (contact@example.com)",
    language="en"
)

# HTML extract format (summary and section text returned as HTML fragments)
wiki_html = wikipediaapi.Wikipedia(
    user_agent="MyProject/1.0 (contact@example.com)",
    language="cs",
    extract_format=wikipediaapi.ExtractFormat.HTML,
)

# Forward extra parameters to every API request (e.g. auto-follow redirects)
wiki_extra = wikipediaapi.Wikipedia(
    user_agent="MyProject/1.0 (contact@example.com)",
    language="en",
    extra_api_params={"redirects": "1"},
)

# Async client — same options, use AsyncWikipedia instead
wiki_async = wikipediaapi.AsyncWikipedia(
    user_agent="MyProject/1.0 (contact@example.com)",
    language="en"
)
```

> **User-Agent is required.** MediaWiki blocks requests without a descriptive
> `User-Agent`. Use the format `AppName/Version (contact)`.

## Quick Start

```python
import wikipediaapi

wiki = wikipediaapi.Wikipedia(
    user_agent="MyProject/1.0 (contact@example.com)",
    language="en"
)

page = wiki.page("Python (programming language)")
if page.exists():
    print(page.title)
    print(page.summary[:200])
```

---

## Further Reading

- [python-sync.md](python-sync.md) — Full synchronous API reference with examples
- [python-async.md](python-async.md) — Full asynchronous API reference with examples
- [bash.md](bash.md) — CLI command reference with examples
