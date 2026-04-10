# Wikipedia-API — Python (Synchronous)

See [README.md](README.md) for installation and client initialization.

Full working example: [`examples/example_sync.py`](../examples/example_sync.py)

---

## Fetching a Page

`wiki.page()` creates a lazy stub — no network call happens until an attribute is read.

```python
page = wiki.page("Python_(programming_language)")

# article() is a convenience alias; unquote=True decodes percent-encoded titles
wiki_hi = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="hi")
page_hi = wiki_hi.article(
    title="%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
    unquote=True,
)
print(page_hi.title)
print(page_hi.summary[:60])
```

---

## Attributes Without a Network Call

Available immediately after `wiki.page()`, no fetch needed:

```python
print(page.title)      # title as supplied to page()
print(page.ns)         # integer namespace number (0 = main article)
print(page.namespace)  # same as ns
print(page.language)   # two-letter language code
print(page.variant)    # language variant, or None
```

---

## Page Existence

```python
# exists() returns True when pageid > 0; triggers an info fetch if not yet done
print(page.exists())   # True

missing = wiki.page("Wikipedia-API-FooBar-DoesNotExist")
print(missing.exists())  # False
print(missing.pageid)    # negative value
```

---

## Page Metadata

Accessing any of these triggers the info API call, which populates all of
them at once and caches them.

```python
print(page.pageid)               # MediaWiki numeric page ID
print(page.fullurl)              # canonical read URL
print(page.editurl)              # URL for editing in the browser
print(page.canonicalurl)         # canonical URL (often same as fullurl)
print(page.displaytitle)         # formatted display title (may contain HTML)
print(page.contentmodel)         # content model, usually "wikitext"
print(page.pagelanguage)         # BCP-47 language code of the page content
print(page.pagelanguagehtmlcode) # HTML lang attribute value
print(page.pagelanguagedir)      # text direction: "ltr" or "rtl"
print(page.touched)              # ISO 8601 timestamp of last cache invalidation
print(page.lastrevid)            # revision ID of the most recent edit
print(page.length)               # page size in bytes
print(page.talkid)               # page ID of the associated talk page
print(page.protection)           # list of active protection descriptors
print(page.restrictiontypes)     # list of applicable protection types
print(page.watchers)             # number of users watching (may be None)
print(page.visitingwatchers)     # watchers who recently visited
print(page.notificationtimestamp)# timestamp of last notification-triggering change
print(page.readable)             # non-empty string if page is readable
print(page.preload)              # preload template name, or None
print(page.varianttitles)        # dict of variant code → variant-specific title
```

---

## Summary and Full Text

```python
# summary — introductory text before the first section heading
print(page.summary[:200])

# text — summary followed by all section content
print(page.text[:200])
```

---

## Sections

```python
def print_sections(sections, level=0):
    for sec in sections:
        indent = "  " * level
        # sec.title  — section heading text
        # sec.level  — heading depth (1 = ==, 2 = ===, …)
        # sec.text   — body text of this section only (not sub-sections)
        # sec.sections — list of child WikipediaPageSection objects
        print(f"{indent}[{sec.level}] {sec.title} ({len(sec.text)} chars)")
        print_sections(sec.sections, level + 1)

print_sections(page.sections)

# section_by_title() — returns the last section matching the heading, or None
section = page.section_by_title("Features and philosophy")
if section:
    print(section.title)
    print(section.text[:80])
    print(section.full_text()[:80])  # heading + body + all descendant sections

# sections_by_title() — returns ALL sections at any depth matching the heading
history_sections = page.sections_by_title("History")
print(f"Sections titled 'History': {len(history_sections)}")
```

---

## Language Links

```python
# langlinks — dict of language code → WikipediaPage stub pre-populated with fullurl
langlinks = page.langlinks
print(f"Language links: {len(langlinks)}")
for code in sorted(langlinks)[:3]:
    lp = langlinks[code]
    print(f"  {code}: {lp.title} — {lp.fullurl}")

# Following a language link to another Wikipedia
wiki_de = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="de")
de_page = wiki_de.page("Deutsche Sprache")
en_page = de_page.langlinks["en"]
print(en_page.summary[:80])
```

---

## Links and Backlinks

```python
# links — dict of title → WikipediaPage stub for every internal link
links = page.links
print(f"Links: {len(links)}")
for title in sorted(links)[:3]:
    print(f"  {title}")

# backlinks — dict of title → WikipediaPage stub for pages linking to this one
backlinks = page.backlinks
print(f"Backlinks: {len(backlinks)}")
for title in sorted(backlinks)[:3]:
    print(f"  {title}")
```

---

## Categories

```python
# categories — dict of category title → WikipediaPage stub
categories = page.categories
print(f"Categories: {len(categories)}")
for title in sorted(categories)[:3]:
    print(f"  {title}")
```

---

## Category Members

```python
import wikipediaapi

# categorymembers — only meaningful on category pages (ns == Namespace.CATEGORY)
cat = wiki.page("Category:Physics")

def print_categorymembers(members, level=0, max_level=1):
    for c in members.values():
        print("{}* {} (ns: {})".format("  " * level, c.title, c.ns))
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            print_categorymembers(c.categorymembers, level + 1, max_level)

print_categorymembers(cat.categorymembers, max_level=1)
```

---

## HTML Extract Format

```python
wiki_html = wikipediaapi.Wikipedia(
    user_agent=USER_AGENT,
    language="cs",
    extract_format=wikipediaapi.ExtractFormat.HTML,
)
page_ostrava = wiki_html.page("Ostrava")
print(page_ostrava.summary[:120])   # HTML fragment

section = page_ostrava.section_by_title("Heraldický znak")
if section:
    print(section.text[:80])        # HTML fragment
```

---

## Language Variants

```python
# variant="zh-cn" — Simplified Chinese
wiki_zh_cn = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="zh", variant="zh-cn")
zh_page_cn = wiki_zh_cn.page("Python")
print(zh_page_cn.title, "— variant:", zh_page_cn.variant)

# variant="zh-tw" — Traditional Chinese
wiki_zh_tw = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="zh", variant="zh-tw")
zh_page_tw = wiki_zh_tw.page("Python")
print(zh_page_tw.title, "— variant:", zh_page_tw.variant)
```

---

## Coordinates

```python
from wikipediaapi import CoordinatesProp, coordinates_prop2str

london = wiki.page("London")

# Fetch primary coordinates (default)
coords = wiki.coordinates(london)
for c in coords:
    print(f"lat={c.lat}, lon={c.lon}, primary={c.primary}, globe={c.globe}")

# Fetch all coordinates (primary + secondary)
coords_all = wiki.coordinates(london, primary="all")

# Page-level property (uses default params, caches on first access)
coords_prop = london.coordinates

# Type-safe selection of extra coordinate fields via enum
from wikipediaapi import CoordinatesProp
coords_rich = wiki.coordinates(
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
imgs = wiki.images(london, direction="descending")
print(f"London images: {len(imgs)}")
for title in sorted(imgs)[:5]:
    print(f"  {title}")

# Page-level property
imgs_prop = london.images

# Individual image metadata — each property triggers a lazy imageinfo fetch
python_page = wiki.page("Python_(programming_language)")
for title, img in sorted(python_page.images.items())[:3]:
    print(f"  {title}:")
    print(f"    URL: {img.url}")
    print(f"    Dimensions: {img.width}x{img.height}")
    print(f"    Size: {img.size} bytes")
    print(f"    MIME: {img.mime}")
    print(f"    Media type: {img.mediatype}")
    print(f"    User: {img.user}")
    print(f"    Timestamp: {img.timestamp}")
    print(f"    Description URL: {img.descriptionurl}")

# Batch-fetch imageinfo for all images at once (more efficient)
infos = python_page.images.imageinfo()
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
# Find pages near a geographic point
results = wiki.geosearch(coord=wikipediaapi.GeoPoint(51.5074, -0.1278), radius=1000, limit=5)
for title, p in results.items():
    meta = p.geosearch_meta
    if meta:
        print(f"  {title}: dist={meta.dist:.1f}m, lat={meta.lat}, lon={meta.lon}, primary={meta.primary}")
```

---

## Random Pages

```python
random_pages = wiki.random(limit=3)
for title in random_pages:
    print(f"  {title}")
```

---

## Search

```python
from wikipediaapi import SearchInfo, SearchProp, SearchQiProfile, SearchSort, SearchWhat

# Basic search
results = wiki.search("Python programming", limit=5)
print(f"{results.totalhits} total hits, suggestion={results.suggestion}")
for title, p in results.pages.items():
    meta = p.search_meta
    if meta:
        print(f"  {title}: size={meta.size}, wordcount={meta.wordcount}, timestamp={meta.timestamp}")
        if meta.snippet:
            print(f"    snippet: {meta.snippet[:100]}")

# Type-safe search with enum parameters
results = wiki.search(
    "Python programming",
    prop=[SearchProp.SIZE, SearchProp.WORDCOUNT, SearchProp.TIMESTAMP, SearchProp.SNIPPET],
    info=[SearchInfo.TOTAL_HITS, SearchInfo.SUGGESTION, SearchInfo.REWRITTEN_QUERY],
    what=SearchWhat.TEXT,
    qi_profile=SearchQiProfile.ENGINE_AUTO_SELECT,
    sort=SearchSort.RELEVANCE,
    limit=5,
)

# Sort by most recently edited
recent = wiki.search("Python", sort=SearchSort.LAST_EDIT_DESC, limit=3)

# Sort by most linked
popular = wiki.search("Python", sort=SearchSort.INCOMING_LINKS_DESC, limit=3)

# Search titles only
title_results = wiki.search("Python", what=SearchWhat.TITLE, limit=5)
```

---

## Batch Operations (PagesDict)

```python
# pages() creates a PagesDict of lazy page stubs
pd = wiki.pages(["London", "Paris", "Berlin"])

# Batch-fetch coordinates for all pages in one API request
batch_coords = pd.coordinates()
for page, coord_list in batch_coords.items():
    print(f"  {page.title}: {len(coord_list)} coordinate(s)")
    for c in coord_list[:2]:
        print(f"    lat={c.lat}, lon={c.lon}, primary={c.primary}, globe={c.globe}")

# Batch-fetch images for all pages in one API request
batch_imgs = pd.images()
for page, img_dict in batch_imgs.items():
    print(f"  {page.title}: {len(img_dict)} image(s)")
    for img_title in sorted(img_dict)[:2]:
        print(f"    {img_title}")

# Batch coordinates with enum properties
from wikipediaapi import CoordinatesProp
batch_coords_rich = pd.coordinates(
    prop=[CoordinatesProp.GLOBE, CoordinatesProp.NAME, CoordinatesProp.DIM]
)
```
