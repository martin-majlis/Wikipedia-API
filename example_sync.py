#!/usr/bin/env python3
"""Comprehensive example of the synchronous Wikipedia-API.

Demonstrates every attribute, property, and method available on
Wikipedia, WikipediaPage, and WikipediaPageSection.
"""

import logging

import wikipediaapi

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
