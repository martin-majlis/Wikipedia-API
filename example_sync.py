#!/usr/bin/env python3
"""Comprehensive example of the synchronous Wikipedia-API.

Demonstrates every attribute, property, and method available on
Wikipedia, WikipediaPage, and WikipediaPageSection.
"""

import logging

import wikipediaapi
from wikipediaapi import coordinates_prop2str
from wikipediaapi import CoordinatesProp
from wikipediaapi import SearchInfo
from wikipediaapi import SearchProp
from wikipediaapi import SearchQiProfile
from wikipediaapi import SearchSort
from wikipediaapi import SearchWhat

# Set to INFO to see the actual API request URLs being made
logging.basicConfig(level=logging.WARNING)

user_agent = "Wikipedia-API Example (merlin@example.com)"

# ──────────────────────────────────────────────────────────────────────────────
# 1. Creating a Wikipedia client
# ──────────────────────────────────────────────────────────────────────────────

# Basic client — English Wikipedia, plain-text (WIKI) extract format
wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language="en")

# Client that returns summary and section text as HTML fragments
wiki_html = wikipediaapi.Wikipedia(
    user_agent=user_agent,
    language="cs",
    extract_format=wikipediaapi.ExtractFormat.HTML,
)

# Client with extra API parameters forwarded to every request
wiki_extra = wikipediaapi.Wikipedia(
    user_agent=user_agent,
    language="en",
    extra_api_params={"redirects": "1"},
)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Fetching a page
# ──────────────────────────────────────────────────────────────────────────────

# page() creates a lazy stub — no network call happens until an attribute is read
page = wiki.page("Python_(programming_language)")

# article() is a convenience alias; unquote=True decodes percent-encoded titles
wiki_hi = wikipediaapi.Wikipedia(user_agent=user_agent, language="hi")
page_hi = wiki_hi.article(
    # https://hi.wikipedia.org/wiki/%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8
    title="%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
    unquote=True,
)
print("Hindi title (decoded):", page_hi.title)
print("Hindi summary (first 60):", page_hi.summary[:60])

# ──────────────────────────────────────────────────────────────────────────────
# 3. Attributes available without any network call (set at construction time)
# ──────────────────────────────────────────────────────────────────────────────

# title — page title as supplied to page() or article()
print("Title (init):", page.title)

# ns — integer namespace number via ATTRIBUTES_MAPPING (set at init, no fetch)
print("NS:", page.ns)

# namespace — same value exposed as an explicit @property
print("Namespace:", page.namespace)

# language — two-letter language code
print("Language:", page.language)

# variant — language variant for auto-conversion, None if not set
print("Variant:", page.variant)

# repr shows title, language, variant, and cached pageid (?? before first fetch)
print("Repr before fetch:", repr(page))

# ──────────────────────────────────────────────────────────────────────────────
# 4. Lazily fetched attributes
#    Accessing any one of these triggers the info API call, which populates
#    all info attributes at once and caches them for subsequent accesses.
# ──────────────────────────────────────────────────────────────────────────────

# pageid — MediaWiki numeric page ID
print("Page ID:", page.pageid)

# repr now shows the resolved page ID and the API-normalised title
print("Repr after fetch:", repr(page))

# title is updated to the API-normalised form after the first fetch
print("Title (normalised):", page.title)

# fullurl — canonical read URL
print("Full URL:", page.fullurl)

# editurl — URL for editing the page in the browser
print("Edit URL:", page.editurl)

# canonicalurl — canonical URL (often identical to fullurl)
print("Canonical URL:", page.canonicalurl)

# displaytitle — formatted display title (may contain HTML markup)
print("Display title:", page.displaytitle)

# contentmodel — content model identifier, usually "wikitext"
print("Content model:", page.contentmodel)

# pagelanguage / pagelanguagehtmlcode / pagelanguagedir — language metadata
print("Page language:", page.pagelanguage)
print("Page language HTML code:", page.pagelanguagehtmlcode)
print("Page language direction:", page.pagelanguagedir)

# touched — timestamp of the last cache invalidation
print("Touched:", page.touched)

# lastrevid — revision ID of the most recent edit
print("Last revision ID:", page.lastrevid)

# length — page size in bytes
print("Length:", page.length)

# talkid — page ID of the associated talk page
print("Talk page ID:", page.talkid)

# protection — list of active protection descriptors (type, level, expiry)
print("Protection:", page.protection)

# restrictiontypes — list of protection types applicable to this page
print("Restriction types:", page.restrictiontypes)

# watchers — number of users watching this page
# (may be None if the wiki does not expose this for the current user)
print("Watchers:", page.watchers)

# visitingwatchers — watchers who recently visited
print("Visiting watchers:", page.visitingwatchers)

# notificationtimestamp — timestamp of the last change that triggered a
# notification (empty string if no notification is pending)
print("Notification timestamp:", page.notificationtimestamp)

# readable — non-empty string if the page is readable (usually "")
print("Readable:", page.readable)

# preload — preload template name if set, otherwise None
print("Preload:", page.preload)

# varianttitles — dict mapping variant codes to variant-specific titles
# (non-empty only on language-variant wikis such as Chinese)
print("Variant titles:", page.varianttitles)

# ──────────────────────────────────────────────────────────────────────────────
# 5. Existence check
# ──────────────────────────────────────────────────────────────────────────────

# exists() returns True when pageid > 0; triggers an info fetch if not yet done
print("Exists:", page.exists())

page_missing = wiki.page("Wikipedia-API-FooBar-DoesNotExist")
print("Missing page exists:", page_missing.exists())
print("Missing page ID:", page_missing.pageid)

# ──────────────────────────────────────────────────────────────────────────────
# 6. Page text — summary, full text, and sections
# ──────────────────────────────────────────────────────────────────────────────

# summary — introductory plain-text excerpt (before the first section heading)
# Accessing summary triggers the extracts API call and populates sections too.
print("Summary (first 120):", page.summary[:120])

# text — full page text: summary followed by all section content
print("Full text (first 120):", page.text[:120])


def print_sections(sections, level=0):
    """Print section hierarchy with indentation.

    Args:
        sections: List of WikipediaPageSection objects
        level: Current indentation level
    """
    for sec in sections:
        indent = "  " * level
        # title — section heading text
        # level — heading depth (1 = top-level ==, 2 = sub-section ===, …)
        # text — body text of this section only, excluding sub-sections
        # sections — list of direct child WikipediaPageSection objects
        print(f"{indent}[{sec.level}] {sec.title} ({len(sec.text)} chars)")
        print_sections(sec.sections, level + 1)


print("Sections:")
print_sections(page.sections)

# section_by_title() — returns the last section matching the given heading, or None
section = page.section_by_title("Features and philosophy")
if section is not None:
    print("Section title:", section.title)
    print("Section level:", section.level)
    print("Section text (first 80):", section.text[:80])
    print("Sub-section count:", len(section.sections))
    # full_text() renders the heading + body text + all descendant sections
    print("Full text (first 80):", section.full_text()[:80])
else:
    print("Section not found.")

# sections_by_title() — returns ALL sections (at any depth) matching the heading
# Useful when the same heading appears in multiple places
history_sections = page.sections_by_title("History")
print(f"Sections titled 'History': {len(history_sections)}")

# ──────────────────────────────────────────────────────────────────────────────
# 7. Related pages
# ──────────────────────────────────────────────────────────────────────────────

# langlinks — dict of language code → WikipediaPage stub for the same topic
langlinks = page.langlinks
print(f"Language links: {len(langlinks)}")
for code in sorted(langlinks)[:3]:  # show first 3 for brevity
    lp = langlinks[code]
    print(f"  {code}: {lp.title} — {lp.fullurl}")

# links — dict of title → WikipediaPage stub for every internal link on the page
links = page.links
print(f"Links: {len(links)}")
for title in sorted(links)[:3]:
    print(f"  {title}")

# backlinks — dict of title → WikipediaPage stub for pages that link to this one
backlinks = page.backlinks
print(f"Backlinks: {len(backlinks)}")
for title in sorted(backlinks)[:3]:
    print(f"  {title}")

# categories — dict of category title → WikipediaPage stub for this page's categories
categories = page.categories
print(f"Categories: {len(categories)}")
for title in sorted(categories)[:3]:
    print(f"  {title}")

# ──────────────────────────────────────────────────────────────────────────────
# 8. Category members
# ──────────────────────────────────────────────────────────────────────────────

# categorymembers — dict of title → WikipediaPage stub for pages in a category
# Only meaningful on category pages (ns == Namespace.CATEGORY)
cat = wiki.page("Category:Physics")
print(f"Category: {cat.title}  (ns={cat.ns})")


def print_categorymembers(members, level=0, max_level=1):
    """Print category members with recursive sub-category exploration.

    Args:
        members: Dictionary of category members
        level: Current indentation level
        max_level: Maximum recursion depth for sub-categories
    """
    for c in members.values():
        print("{}* {} (ns: {})".format("  " * level, c.title, c.ns))
        # Recurse into sub-categories up to max_level deep
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            print_categorymembers(c.categorymembers, level + 1, max_level)


print_categorymembers(cat.categorymembers, max_level=1)

# ──────────────────────────────────────────────────────────────────────────────
# 9. HTML extract format
# ──────────────────────────────────────────────────────────────────────────────

# ExtractFormat.HTML returns summary and section text as HTML fragments
page_ostrava = wiki_html.page("Ostrava")
print("HTML page exists:", page_ostrava.exists())
print("HTML summary (first 120):", page_ostrava.summary[:120])

section_ostrava = page_ostrava.section_by_title("Heraldický znak")
if section_ostrava is not None:
    print("HTML section text (first 80):", section_ostrava.text[:80])
else:
    print("Section not found.")

# ──────────────────────────────────────────────────────────────────────────────
# 10. Following a language link to another Wikipedia
# ──────────────────────────────────────────────────────────────────────────────

wiki_de = wikipediaapi.Wikipedia(user_agent=user_agent, language="de")
de_page = wiki_de.page("Deutsche Sprache")
print("DE page:", de_page.title, "—", de_page.fullurl)

# Jump to the English version via langlinks
en_page = de_page.langlinks["en"]
print("EN page:", en_page.title, "—", en_page.fullurl)
print("EN summary (first 80):", en_page.summary[:80])

# ──────────────────────────────────────────────────────────────────────────────
# 11. Language variants (Chinese)
# ──────────────────────────────────────────────────────────────────────────────

# Without variant — returns content in the default script
wiki_zh = wikipediaapi.Wikipedia(user_agent=user_agent, language="zh")
zh_page = wiki_zh.page("Python")
print("ZH (no variant):", zh_page.title, "—", zh_page.fullurl)
print("ZH variant titles:", zh_page.varianttitles)

# variant="zh-cn" — Simplified Chinese
# https://zh.wikipedia.org/zh-cn/Python
wiki_zh_cn = wikipediaapi.Wikipedia(user_agent=user_agent, language="zh", variant="zh-cn")
zh_page_cn = wiki_zh_cn.page("Python")
print("ZH-CN:", zh_page_cn.title, "— variant:", zh_page_cn.variant)

# variant="zh-tw" — Traditional Chinese
# https://zh.wikipedia.org/zh-tw/Python
wiki_zh_tw = wikipediaapi.Wikipedia(user_agent=user_agent, language="zh", variant="zh-tw")
zh_page_tw = wiki_zh_tw.page("Python")
print("ZH-TW:", zh_page_tw.title, "— variant:", zh_page_tw.variant)

# variant="zh-sg" — Simplified Chinese (Singapore)
# https://zh.wikipedia.org/zh-sg/Python
wiki_zh_sg = wikipediaapi.Wikipedia(user_agent=user_agent, language="zh", variant="zh-sg")
zh_page_sg = wiki_zh_sg.page("Python")
print("ZH-SG:", zh_page_sg.title, "— variant:", zh_page_sg.variant)

# ──────────────────────────────────────────────────────────────────────────────
# 12. Coordinates (prop=coordinates)
# ──────────────────────────────────────────────────────────────────────────────

# Fetch geographic coordinates for a page (default: primary only)
london = wiki.page("London")
coords = wiki.coordinates(london)
print(f"London coordinates ({len(coords)}):")
for c in coords:
    print(f"  lat={c.lat}, lon={c.lon}, primary={c.primary}, globe={c.globe}")

# Fetch all coordinates (primary + secondary) with custom params
coords_all = wiki.coordinates(london, primary="all")
print(f"London all coordinates: {len(coords_all)}")

# Page-level property (uses default params, triggers fetch on first access)
coords_prop = london.coordinates
print(f"London coords via property: {len(coords_prop)}")

# ──────────────────────────────────────────────────────────────────────────────
# 12.1. Coordinates with Properties Enum (NEW)
# ──────────────────────────────────────────────────────────────────────────────

# Using enum values for type-safe coordinate property selection
print("\n--- Coordinates with Enum Properties ---")

# Single property using enum
coords_enum_single = wiki.coordinates(london, prop=[CoordinatesProp.GLOBE])  # type: ignore
print(f"London with GLOBE property: {len(coords_enum_single)} coordinates")

# Multiple properties using enum values
coords_enum_multi = wiki.coordinates(
    london, prop=[CoordinatesProp.GLOBE, CoordinatesProp.NAME, CoordinatesProp.TYPE]  # type: ignore
)
print(f"London with GLOBE+NAME+TYPE properties: {len(coords_enum_multi)} coordinates")
for c in coords_enum_multi:
    print(
        f"  lat={c.lat}, lon={c.lon}, name={getattr(c, 'name', 'N/A')}, type={getattr(c, 'type', 'N/A')}"
    )

# Mixed enum and string values (backward compatible)
coords_mixed = wiki.coordinates(
    london, prop=[CoordinatesProp.GLOBE, "name", "type"]  # type: ignore
)
print(f"London with mixed enum+string properties: {len(coords_mixed)} coordinates")

# Using the converter function directly
print("\n--- Converter Function Examples ---")
print(
    f"coordinates_prop2str(CoordinatesProp.GLOBE) = {coordinates_prop2str(CoordinatesProp.GLOBE)}"
)
print(f"coordinates_prop2str('globe') = {coordinates_prop2str('globe')}")
print(f"coordinates_prop2str('custom') = {coordinates_prop2str('custom')}")

# All available enum values
print(f"\nAll CoordinatesProp values: {[prop.value for prop in CoordinatesProp]}")

# ──────────────────────────────────────────────────────────────────────────────
# 12.2. Batch Coordinates with Enum Properties (NEW)
# ──────────────────────────────────────────────────────────────────────────────

# Batch coordinates with enum properties
print("\n--- Batch Coordinates with Enum Properties ---")
pages = wiki.pages(["London", "Paris", "Berlin"])

# Using enum values for batch coordinates
batch_coords_enum = pages.coordinates(
    prop=[CoordinatesProp.GLOBE, CoordinatesProp.NAME, CoordinatesProp.DIM]  # type: ignore
)
for page, coord_list in batch_coords_enum.items():
    print(f"  {page.title}: {len(coord_list)} coordinate(s) with GLOBE+NAME+DIM")
    for c in coord_list[:2]:  # Show first 2 coordinates
        print(
            f"    lat={c.lat}, lon={c.lon}, name={getattr(c, 'name', 'N/A')}, dim={getattr(c, 'dim', 'N/A')}"
        )

# Backward-compatible string usage still works
batch_coords_strings = pages.coordinates(prop=["globe", "name", "dim"])
print(f"Batch coordinates with strings: {len(batch_coords_strings)} pages")

# ──────────────────────────────────────────────────────────────────────────────
# 13. Images (prop=images)
# ──────────────────────────────────────────────────────────────────────────────

# Fetch images/files used on a page (using direction)
imgs = wiki.images(london, direction="descending")
print(f"London images ({len(imgs)}):")
for title in sorted(imgs)[:5]:
    print(f"  {title}")

# Page-level property
imgs_prop = london.images
print(f"London images via property: {len(imgs_prop)}")

# ──────────────────────────────────────────────────────────────────────────────
# 14. Geosearch (list=geosearch)
# ──────────────────────────────────────────────────────────────────────────────

# Find pages near a geographic point
results = wiki.geosearch(coord=wikipediaapi.GeoPoint(51.5074, -0.1278), radius=1000, limit=5)
print(f"Geosearch results ({len(results)}):")
for title, p in results.items():
    meta = p.geosearch_meta
    if meta:
        print(f"  {title}: dist={meta.dist:.1f}m, lat={meta.lat}, lon={meta.lon}")

# ──────────────────────────────────────────────────────────────────────────────
# 15. Random pages (list=random)
# ──────────────────────────────────────────────────────────────────────────────

random_pages = wiki.random(limit=3)
print(f"Random pages ({len(random_pages)}):")
for title in random_pages:
    print(f"  {title}")

# ──────────────────────────────────────────────────────────────────────────────
# 16. Search (list=search) with Type-Safe Enums
# ──────────────────────────────────────────────────────────────────────────────

# Basic search (backward compatible)
search_results = wiki.search("Python programming", limit=5)
print(f"Search: {search_results.totalhits} total hits, suggestion={search_results.suggestion}")
print(f"Search results ({len(search_results.pages)}):")
for title, p in search_results.pages.items():
    meta = p.search_meta
    if meta:
        print(f"  {title}: size={meta.size}, wordcount={meta.wordcount}")

# Type-safe search with comprehensive enum parameters
enum_search_results = wiki.search(
    "Python programming",
    prop=[SearchProp.SIZE, SearchProp.WORDCOUNT, SearchProp.TIMESTAMP, SearchProp.SNIPPET],
    info=[SearchInfo.TOTAL_HITS, SearchInfo.SUGGESTION, SearchInfo.REWRITTEN_QUERY],
    what=SearchWhat.TEXT,
    qi_profile=SearchQiProfile.ENGINE_AUTO_SELECT,
    sort=SearchSort.RELEVANCE,
    limit=5,
)
print(f"Enum search: {enum_search_results.totalhits} total hits")
print(f"Enum search results ({len(enum_search_results.pages)}):")
for title, p in enum_search_results.pages.items():
    meta = p.search_meta
    if meta:
        print(
            f"  {title}: size={meta.size}, wordcount={meta.wordcount}, timestamp={meta.timestamp}"
        )

# Search by title only
title_search = wiki.search("Python", what=SearchWhat.TITLE, limit=5)
print(f"Title search: {title_search.totalhits} total hits")

# Different sort strategies
recent_search = wiki.search("Python", sort=SearchSort.LAST_EDIT_DESC, limit=3)
print(f"Most recently edited: {len(recent_search.pages)} pages")

popular_search = wiki.search("Python", sort=SearchSort.INCOMING_LINKS_DESC, limit=3)
print(f"Most linked: {len(popular_search.pages)} pages")

# Mixed enum and string usage (fully supported)
mixed_search = wiki.search(
    "Python",
    prop=[SearchProp.SIZE, "wordcount"],  # Mixed enum and string
    info=[SearchInfo.TOTAL_HITS, "suggestion"],  # Mixed enum and string
    what=SearchWhat.TEXT,
    qi_profile="engine_autoselect",  # String
    sort="relevance",  # String
)
print(f"Mixed search: {mixed_search.totalhits} total hits")

# ──────────────────────────────────────────────────────────────────────────────
# 17. Batch methods and PagesDict
# ──────────────────────────────────────────────────────────────────────────────

# pages() creates a PagesDict of lazy page stubs
pd = wiki.pages(["London", "Paris", "Berlin"])
print(f"PagesDict: {len(pd)} pages")

# Batch-fetch coordinates for all pages at once (efficient multi-title request)
batch_coords = pd.coordinates()
for page, coord_list in batch_coords.items():
    print(f"  {page.title}: {len(coord_list)} coordinate(s)")

# Batch-fetch images for all pages at once
batch_imgs = pd.images()
for title, img_dict in batch_imgs.items():
    print(f"  {title}: {len(img_dict)} image(s)")
