# Wikipedia-API — Python (Asynchronous)

See [README.md](README.md) for installation and client initialization.

Full working example: [`examples/example_async.py`](../examples/example_async.py)

---

## Key Differences from Synchronous API

| Sync                | Async                     |
| ------------------- | ------------------------- |
| `Wikipedia(...)`    | `AsyncWikipedia(...)`     |
| `page.summary`      | `await page.summary`      |
| `page.fullurl`      | `await page.fullurl`      |
| `page.exists()`     | `await page.exists()`     |
| `wiki.pages([...])` | `await wiki.pages([...])` |
| `pd.coordinates()`  | `await pd.coordinates()`  |

**Plain `@property` (no await):** `title`, `ns`, `namespace`, `language`, `variant`

**Sync methods (no await):** `section_by_title()`, `sections_by_title()`

All other attributes and methods are awaitable.

---

## Client and Page Creation

```python
import asyncio
import wikipediaapi

async def main():
    wiki = wikipediaapi.AsyncWikipedia(
        user_agent="MyProject/1.0 (contact@example.com)",
        language="en"
    )

    # page() is synchronous — no network call yet
    page = wiki.page("Python_(programming_language)")

    # article() with percent-encoded title
    wiki_hi = wikipediaapi.AsyncWikipedia(user_agent=USER_AGENT, language="hi")
    page_hi = wiki_hi.article(
        title="%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
        unquote=True,
    )
    print(page_hi.title)                    # plain @property — no await
    print((await page_hi.summary)[:60])     # awaitable property

asyncio.run(main())
```

---

## Attributes Without a Network Call

```python
print(page.title)      # plain @property
print(page.ns)         # plain @property
print(page.namespace)  # plain @property
print(page.language)   # plain @property
print(page.variant)    # plain @property
```

---

## Page Existence

```python
print(await page.exists())   # True

missing = wiki.page("Wikipedia-API-FooBar-DoesNotExist")
print(await missing.exists())  # False
print(await missing.pageid)    # negative value
```

---

## Page Metadata

```python
print(await page.pageid)               # MediaWiki numeric page ID
print(await page.fullurl)              # canonical read URL
print(await page.editurl)              # URL for editing in the browser
print(await page.canonicalurl)         # canonical URL
print(await page.displaytitle)         # formatted display title
print(await page.contentmodel)         # usually "wikitext"
print(await page.pagelanguage)         # BCP-47 language code
print(await page.pagelanguagehtmlcode) # HTML lang attribute value
print(await page.pagelanguagedir)      # "ltr" or "rtl"
print(await page.touched)              # ISO 8601 timestamp of last cache invalidation
print(await page.lastrevid)            # revision ID of the most recent edit
print(await page.length)               # page size in bytes
print(await page.talkid)               # page ID of the associated talk page
print(await page.protection)           # list of active protection descriptors
print(await page.restrictiontypes)     # list of applicable protection types
print(await page.watchers)             # number of users watching (may be None)
print(await page.visitingwatchers)     # watchers who recently visited
print(await page.notificationtimestamp)
print(await page.readable)
print(await page.preload)
print(await page.varianttitles)        # dict of variant code → variant-specific title
```

---

## Summary and Full Text

```python
summary = await page.summary
print(summary[:200])

text = await page.text
print(text[:200])
```

---

## Sections

```python
sections = await page.sections    # awaitable property

def print_sections(sections, level=0):
    for sec in sections:
        indent = "  " * level
        print(f"{indent}[{sec.level}] {sec.title} ({len(sec.text)} chars)")
        print_sections(sec.sections, level + 1)

print_sections(sections)

# section_by_title() and sections_by_title() are synchronous
# (sections are already cached after await page.sections)
section = page.section_by_title("Features and philosophy")
if section:
    print(section.title)
    print(section.text[:80])
    print(section.full_text()[:80])

history_sections = page.sections_by_title("History")
print(f"Sections titled 'History': {len(history_sections)}")
```

---

## Language Links

```python
langlinks = await page.langlinks
print(f"Language links: {len(langlinks)}")
for code in sorted(langlinks)[:3]:
    lp = langlinks[code]
    print(f"  {code}: {lp.title} — {await lp.fullurl}")

# Following a language link
wiki_de = wikipediaapi.AsyncWikipedia(user_agent=USER_AGENT, language="de")
de_page = wiki_de.page("Deutsche Sprache")
de_langlinks = await de_page.langlinks
en_page = de_langlinks["en"]
print(await en_page.fullurl)
print((await en_page.summary)[:80])
```

---

## Links and Backlinks

```python
links = await page.links
print(f"Links: {len(links)}")
for title in sorted(links)[:3]:
    print(f"  {title}")

backlinks = await page.backlinks
print(f"Backlinks: {len(backlinks)}")
for title in sorted(backlinks)[:3]:
    print(f"  {title}")
```

---

## Categories

```python
categories = await page.categories
print(f"Categories: {len(categories)}")
for title in sorted(categories)[:3]:
    print(f"  {title}")
```

---

## Category Members

```python
import wikipediaapi

cat = wiki.page("Category:Physics")

async def print_categorymembers(members, level=0, max_level=1):
    for c in members.values():
        print("{}* {} (ns: {})".format("  " * level, c.title, c.ns))
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            await print_categorymembers(await c.categorymembers, level + 1, max_level)

await print_categorymembers(await cat.categorymembers, max_level=1)
```

---

## HTML Extract Format

```python
wiki_html = wikipediaapi.AsyncWikipedia(
    user_agent=USER_AGENT,
    language="cs",
    extract_format=wikipediaapi.ExtractFormat.HTML,
)
page_ostrava = wiki_html.page("Ostrava")
summary_ostrava = await page_ostrava.summary
print(summary_ostrava[:120])   # HTML fragment

# section_by_title() is synchronous after sections are cached
section_ostrava = page_ostrava.section_by_title("Heraldický znak")
if section_ostrava:
    print(section_ostrava.text[:80])
```

---

## Language Variants

```python
wiki_zh_cn = wikipediaapi.AsyncWikipedia(user_agent=USER_AGENT, language="zh", variant="zh-cn")
zh_page_cn = wiki_zh_cn.page("Python")
print(zh_page_cn.title, "— variant:", zh_page_cn.variant)  # plain @property

wiki_zh_tw = wikipediaapi.AsyncWikipedia(user_agent=USER_AGENT, language="zh", variant="zh-tw")
zh_page_tw = wiki_zh_tw.page("Python")
print(zh_page_tw.title, "— variant:", zh_page_tw.variant)
```

---

## Coordinates

```python
from wikipediaapi import CoordinatesProp

london = wiki.page("London")

# Fetch primary coordinates
coords = await wiki.coordinates(london)
for c in coords:
    print(f"lat={c.lat}, lon={c.lon}, primary={c.primary}, globe={c.globe}")

# Fetch all coordinates
coords_all = await wiki.coordinates(london, primary="all")

# Page-level awaitable property
coords_prop = await london.coordinates

# Type-safe selection of extra coordinate fields via enum
coords_rich = await wiki.coordinates(
    london,
    prop=[CoordinatesProp.GLOBE, CoordinatesProp.NAME, CoordinatesProp.TYPE],
)
for c in coords_rich:
    print(f"lat={c.lat}, lon={c.lon}, name={getattr(c, 'name', None)}, type={getattr(c, 'type', None)}")
```

---

## Images and Image Metadata

```python
# Images used on a page
london = wiki.page("London")
imgs = await wiki.images(london, direction="descending")
for title in sorted(imgs)[:5]:
    print(f"  {title}")

# Page-level awaitable property
imgs_prop = await london.images

# Individual image metadata — each property is awaitable
python_page = wiki.page("Python_(programming_language)")
for title, img in sorted((await python_page.images).items())[:3]:
    print(f"  {title}:")
    print(f"    URL: {await img.url}")
    print(f"    Dimensions: {await img.width}x{await img.height}")
    print(f"    Size: {await img.size} bytes")
    print(f"    MIME: {await img.mime}")
    print(f"    Media type: {await img.mediatype}")
    print(f"    User: {await img.user}")
    print(f"    Timestamp: {await img.timestamp}")
    print(f"    Description URL: {await img.descriptionurl}")

# Batch-fetch imageinfo for all images at once (more efficient)
infos = await (await python_page.images).imageinfo()
print(f"Batch imageinfo: {len(infos)} images")
for title, info_list in sorted(infos.items())[:3]:
    if info_list:
        info = info_list[0]
        print(f"  {title}:")
        print(f"    URL: {info.url}")
        print(f"    Dimensions: {info.width}x{info.height}")
        print(f"    Size: {info.size} bytes")
        print(f"    MIME: {info.mime}")
        print(f"    Media type: {info.mediatype}")
        print(f"    User: {info.user}")
        print(f"    Timestamp: {info.timestamp}")
```

---

## Geosearch

```python
results = await wiki.geosearch(
    coord=wikipediaapi.GeoPoint(51.5074, -0.1278), radius=1000, limit=5
)
for title, p in results.items():
    meta = p.geosearch_meta
    if meta:
        print(f"  {title}: dist={meta.dist:.1f}m, lat={meta.lat}, lon={meta.lon}, primary={meta.primary}")
```

---

## Random Pages

```python
random_pages = await wiki.random(limit=3)
for title in random_pages:
    print(f"  {title}")
```

---

## Search

```python
results = await wiki.search("Python programming", limit=5)
print(f"{results.totalhits} total hits, suggestion={results.suggestion}")
for title, p in results.pages.items():
    meta = p.search_meta
    if meta:
        print(f"  {title}: size={meta.size}, wordcount={meta.wordcount}, timestamp={meta.timestamp}")
        if meta.snippet:
            print(f"    snippet: {meta.snippet[:100]}")
```

---

## Batch Operations (AsyncPagesDict)

```python
# pages() is awaitable and returns an AsyncPagesDict
pd = await wiki.pages(["London", "Paris", "Berlin"])

# Batch-fetch coordinates for all pages in one API request
batch_coords = await pd.coordinates()
for page, coord_list in batch_coords.items():
    print(f"  {page.title}: {len(coord_list)} coordinate(s)")
    for c in coord_list[:2]:
        print(f"    lat={c.lat}, lon={c.lon}, primary={c.primary}, globe={c.globe}")

# Batch-fetch images for all pages in one API request
batch_imgs = await pd.images()
for page, img_dict in batch_imgs.items():
    print(f"  {page.title}: {len(img_dict)} image(s)")
    for img_title in sorted(img_dict)[:2]:
        print(f"    {img_title}")

# Concurrent fetching with asyncio.gather
import asyncio
london = wiki.page("London")
paris = wiki.page("Paris")
london_summary, paris_summary = await asyncio.gather(london.summary, paris.summary)
print(london_summary[:80])
print(paris_summary[:80])
```
