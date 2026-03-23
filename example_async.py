#!/usr/bin/env python3
"""Comprehensive example of the asynchronous Wikipedia-API.

Demonstrates every attribute, property, and method available on
AsyncWikipedia, AsyncWikipediaPage, and WikipediaPageSection.

Key differences from the synchronous API:
  - Info-only attributes (fullurl, displaytitle, …) are awaitable:
      url = await page.fullurl
  - Multi-source attributes (pageid) are also awaitable:
      pid = await page.pageid
  - Data properties (summary, sections, text, langlinks, links, backlinks, categories,
    categorymembers) are awaitable properties (no parentheses):
      links = await page.links
      sections = await page.sections
  - title, ns, language, variant are plain @property values (no await needed).
  - exists() is a coroutine method — use: exists = await page.exists()
  - section_by_title() and sections_by_title() are plain synchronous methods.
"""

import asyncio
import logging

import wikipediaapi

# Set to INFO to see the actual API request URLs being made
logging.basicConfig(level=logging.WARNING)

user_agent = "Wikipedia-API Example (merlin@example.com)"


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


async def print_categorymembers(members, level=0, max_level=1):
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
            await print_categorymembers(await c.categorymembers, level + 1, max_level)


async def main():
    """Demonstrate AsyncWikipedia API usage with various examples.

    Shows page creation, property access, section navigation,
    and category traversal using async/await patterns.
    """
    # ──────────────────────────────────────────────────────────────────────────
    # 1. Creating an AsyncWikipedia client
    # ──────────────────────────────────────────────────────────────────────────

    # Basic client — English Wikipedia, plain-text (WIKI) extract format
    wiki = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="en")

    # Client that returns summary and section text as HTML fragments
    wiki_html = wikipediaapi.AsyncWikipedia(
        user_agent=user_agent,
        language="cs",
        extract_format=wikipediaapi.ExtractFormat.HTML,
    )

    # Client with extra API parameters forwarded to every request
    wiki_extra = wikipediaapi.AsyncWikipedia(  # noqa: F841
        user_agent=user_agent,
        language="en",
        extra_api_params={"redirects": "1"},
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Fetching a page
    # ──────────────────────────────────────────────────────────────────────────

    # page() creates a lazy stub — no network call happens until an attribute
    # or method is awaited
    page = wiki.page("Python_(programming_language)")

    # article() is a convenience alias; unquote=True decodes percent-encoded titles
    wiki_hi = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="hi")
    page_hi = wiki_hi.article(
        # https://hi.wikipedia.org/wiki/%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8
        title="%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
        unquote=True,
    )
    print("Hindi title (decoded):", page_hi.title)
    print("Hindi summary (first 60):", (await page_hi.summary)[:60])

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Attributes available without any network call (set at construction time)
    # ──────────────────────────────────────────────────────────────────────────

    # title — page title as supplied to page() or article(); plain @property
    print("Title (init):", page.title)

    # ns — integer namespace number; plain @property (set at init, no await)
    print("NS:", page.ns)

    # namespace — alias for ns; plain @property
    print("Namespace:", page.namespace)

    # language — two-letter language code; plain @property
    print("Language:", page.language)

    # variant — language variant for auto-conversion, None if not set; @property
    print("Variant:", page.variant)

    # repr shows title, language, variant, and cached pageid (?? before fetch)
    print("Repr before fetch:", repr(page))

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Lazily fetched attributes — always use await
    #    Info-only attributes trigger the info API call on first await.
    #    Multi-source attributes (pageid) trigger their first listed source.
    #    Once fetched, the value is cached; subsequent awaits return immediately.
    # ──────────────────────────────────────────────────────────────────────────

    # pageid — MediaWiki numeric page ID (multi-source, fetches info on first await)
    print("Page ID:", await page.pageid)

    # repr now shows the resolved page ID and the API-normalised title
    print("Repr after fetch:", repr(page))

    # title is updated to the API-normalised form after the first fetch
    print("Title (normalised):", page.title)

    # fullurl — canonical read URL (info-only, fetches info if not yet done)
    print("Full URL:", await page.fullurl)

    # editurl — URL for editing the page in the browser
    print("Edit URL:", await page.editurl)

    # canonicalurl — canonical URL (often identical to fullurl)
    print("Canonical URL:", await page.canonicalurl)

    # displaytitle — formatted display title (may contain HTML markup)
    print("Display title:", await page.displaytitle)

    # contentmodel — content model identifier, usually "wikitext"
    print("Content model:", await page.contentmodel)

    # pagelanguage / pagelanguagehtmlcode / pagelanguagedir — language metadata
    print("Page language:", await page.pagelanguage)
    print("Page language HTML code:", await page.pagelanguagehtmlcode)
    print("Page language direction:", await page.pagelanguagedir)

    # touched — timestamp of the last cache invalidation
    print("Touched:", await page.touched)

    # lastrevid — revision ID of the most recent edit
    print("Last revision ID:", await page.lastrevid)

    # length — page size in bytes
    print("Length:", await page.length)

    # talkid — page ID of the associated talk page
    print("Talk page ID:", await page.talkid)

    # protection — list of active protection descriptors (type, level, expiry)
    print("Protection:", await page.protection)

    # restrictiontypes — list of protection types applicable to this page
    print("Restriction types:", await page.restrictiontypes)

    # watchers — number of users watching this page
    # (may be None if the wiki does not expose this for the current user)
    print("Watchers:", await page.watchers)

    # visitingwatchers — watchers who recently visited
    print("Visiting watchers:", await page.visitingwatchers)

    # notificationtimestamp — timestamp of the last change that triggered a
    # notification (empty string if no notification is pending)
    print("Notification timestamp:", await page.notificationtimestamp)

    # readable — non-empty string if the page is readable (usually "")
    print("Readable:", await page.readable)

    # preload — preload template name if set, otherwise None
    print("Preload:", await page.preload)

    # varianttitles — dict mapping variant codes to variant-specific titles
    # (non-empty only on language-variant wikis such as Chinese)
    print("Variant titles:", await page.varianttitles)

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Existence check
    # ──────────────────────────────────────────────────────────────────────────

    # exists() is a coroutine — it lazily fetches pageid via the info API call
    # (same approach as await page.fullurl); no prior fetch is needed
    print("Exists:", await page.exists())

    page_missing = wiki.page("Wikipedia-API-FooBar-DoesNotExist")
    print("Missing page exists:", await page_missing.exists())
    print("Missing page ID:", await page_missing.pageid)

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Page text — summary and sections
    # ──────────────────────────────────────────────────────────────────────────

    # summary is an awaitable property that fetches and returns the introductory text
    summary = await page.summary
    print("Summary (first 120):", summary[:120])

    # text — full page text: summary followed by all section content
    text = await page.text
    print("Full text (first 120):", text[:120])

    # sections is now an awaitable property that auto-fetches via extracts
    sections = await page.sections
    print("Sections:")
    print_sections(sections)

    # section_by_title() — plain sync method, returns last matching section or None
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

    # sections_by_title() — returns ALL sections matching the heading (any depth)
    # Useful when the same heading appears in multiple sub-sections
    history_sections = page.sections_by_title("History")
    print(f"Sections titled 'History': {len(history_sections)}")

    # ──────────────────────────────────────────────────────────────────────────
    # 7. Related pages — all collection properties are awaitables
    # ──────────────────────────────────────────────────────────────────────────

    # langlinks — awaitable property returning dict of language code → AsyncWikipediaPage
    langlinks = await page.langlinks
    print(f"Language links: {len(langlinks)}")
    for code in sorted(langlinks)[:3]:  # show first 3 for brevity
        lp = langlinks[code]
        print(f"  {code}: {lp.title} — {await lp.fullurl}")

    # links — awaitable property returning dict of title → AsyncWikipediaPage stub
    links = await page.links
    print(f"Links: {len(links)}")
    for title in sorted(links)[:3]:
        print(f"  {title}")

    # backlinks — awaitable property returning dict of title → AsyncWikipediaPage stub
    backlinks = await page.backlinks
    print(f"Backlinks: {len(backlinks)}")
    for title in sorted(backlinks)[:3]:
        print(f"  {title}")

    # categories — awaitable property returning dict of category title → stub page
    categories = await page.categories
    print(f"Categories: {len(categories)}")
    for title in sorted(categories)[:3]:
        print(f"  {title}")

    # ──────────────────────────────────────────────────────────────────────────
    # 8. Category members
    # ──────────────────────────────────────────────────────────────────────────

    # categorymembers — awaitable property; only meaningful on category pages
    cat = wiki.page("Category:Physics")
    print(f"Category: {cat.title}  (ns={cat.ns})")
    await print_categorymembers(await cat.categorymembers, max_level=1)

    # ──────────────────────────────────────────────────────────────────────────
    # 9. HTML extract format
    # ──────────────────────────────────────────────────────────────────────────

    # ExtractFormat.HTML returns summary and section text as HTML fragments
    page_ostrava = wiki_html.page("Ostrava")
    print("HTML page exists:", await page_ostrava.exists())
    summary_ostrava = await page_ostrava.summary
    print("HTML summary (first 120):", summary_ostrava[:120])

    section_ostrava = page_ostrava.section_by_title("Heraldický znak")
    if section_ostrava is not None:
        print("HTML section text (first 80):", section_ostrava.text[:80])
    else:
        print("Section not found.")

    # ──────────────────────────────────────────────────────────────────────────
    # 10. Following a language link to another Wikipedia
    # ──────────────────────────────────────────────────────────────────────────

    wiki_de = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="de")
    de_page = wiki_de.page("Deutsche Sprache")
    # Await the fullurl attribute — triggers the info fetch if not yet done
    print("DE page:", de_page.title, "—", await de_page.fullurl)

    de_langlinks = await de_page.langlinks
    en_page = de_langlinks["en"]
    # fullurl is always a coroutine even when pre-set; await to get the string
    print("EN page:", en_page.title, "—", await en_page.fullurl)
    print("EN summary (first 80):", (await en_page.summary)[:80])

    # ──────────────────────────────────────────────────────────────────────────
    # 11. Language variants (Chinese)
    # ──────────────────────────────────────────────────────────────────────────

    # Without variant — returns content in the default script
    wiki_zh = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="zh")
    zh_page = wiki_zh.page("Python")
    print("ZH (no variant):", zh_page.title, "—", await zh_page.fullurl)
    print("ZH variant titles:", await zh_page.varianttitles)

    # variant="zh-cn" — Simplified Chinese
    # https://zh.wikipedia.org/zh-cn/Python
    wiki_zh_cn = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="zh", variant="zh-cn")
    zh_page_cn = wiki_zh_cn.page("Python")
    print("ZH-CN:", zh_page_cn.title, "— variant:", zh_page_cn.variant)

    # variant="zh-tw" — Traditional Chinese
    # https://zh.wikipedia.org/zh-tw/Python
    wiki_zh_tw = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="zh", variant="zh-tw")
    zh_page_tw = wiki_zh_tw.page("Python")
    print("ZH-TW:", zh_page_tw.title, "— variant:", zh_page_tw.variant)

    # variant="zh-sg" — Simplified Chinese (Singapore)
    # https://zh.wikipedia.org/zh-sg/Python
    wiki_zh_sg = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="zh", variant="zh-sg")
    zh_page_sg = wiki_zh_sg.page("Python")
    print("ZH-SG:", zh_page_sg.title, "— variant:", zh_page_sg.variant)

    # ──────────────────────────────────────────────────────────────────────────
    # 12. Coordinates (prop=coordinates)
    # ──────────────────────────────────────────────────────────────────────────

    # Fetch geographic coordinates for a page (default: primary only)
    london = wiki.page("London")
    coords = await wiki.coordinates(london)
    print(f"London coordinates ({len(coords)}):")
    for c in coords:
        print(f"  lat={c.lat}, lon={c.lon}, primary={c.primary}, globe={c.globe}")

    # Fetch all coordinates (primary + secondary) with custom params
    coords_all = await wiki.coordinates(london, primary="all")
    print(f"London all coordinates: {len(coords_all)}")

    # Page-level awaitable property (uses default params, triggers fetch on first access)
    coords_prop = await london.coordinates
    print(f"London coords via property: {len(coords_prop)}")

    # ──────────────────────────────────────────────────────────────────────────
    # 13. Images (prop=images)
    # ──────────────────────────────────────────────────────────────────────────

    # Fetch images/files used on a page
    imgs = await wiki.images(london)
    print(f"London images ({len(imgs)}):")
    for title in sorted(imgs)[:5]:
        print(f"  {title}")

    # Page-level awaitable property
    imgs_prop = await london.images
    print(f"London images via property: {len(imgs_prop)}")

    # ──────────────────────────────────────────────────────────────────────────
    # 14. Geosearch (list=geosearch)
    # ──────────────────────────────────────────────────────────────────────────

    # Find pages near a geographic point
    results = await wiki.geosearch(coord="51.5074|-0.1278", radius=1000, limit=5)
    print(f"Geosearch results ({len(results)}):")
    for title, p in results.items():
        meta = p.geosearch_meta
        if meta:
            print(f"  {title}: dist={meta.dist:.1f}m, lat={meta.lat}, lon={meta.lon}")

    # ──────────────────────────────────────────────────────────────────────────
    # 15. Random pages (list=random)
    # ──────────────────────────────────────────────────────────────────────────

    random_pages = await wiki.random(limit=3)
    print(f"Random pages ({len(random_pages)}):")
    for title in random_pages:
        print(f"  {title}")

    # ──────────────────────────────────────────────────────────────────────────
    # 16. Search (list=search)
    # ──────────────────────────────────────────────────────────────────────────

    search_results = await wiki.search("Python programming", limit=5)
    print(f"Search: {search_results.totalhits} total hits, suggestion={search_results.suggestion}")
    print(f"Search results ({len(search_results.pages)}):")
    for title, p in search_results.pages.items():
        meta = p.search_meta
        if meta:
            print(f"  {title}: size={meta.size}, wordcount={meta.wordcount}")

    # ──────────────────────────────────────────────────────────────────────────
    # 17. Batch methods and PagesDict
    # ──────────────────────────────────────────────────────────────────────────

    # pages() creates an AsyncPagesDict of lazy page stubs
    pd = wiki.pages(["London", "Paris", "Berlin"])
    print(f"PagesDict: {len(pd)} pages")

    # Batch-fetch coordinates for all pages at once (efficient multi-title request)
    batch_coords = await pd.coordinates()
    for title, coord_list in batch_coords.items():
        print(f"  {title}: {len(coord_list)} coordinate(s)")

    # Batch-fetch images for all pages at once
    batch_imgs = await pd.images()
    for title, img_dict in batch_imgs.items():
        print(f"  {title}: {len(img_dict)} image(s)")


asyncio.run(main())
