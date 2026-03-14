#!/usr/bin/env python3
import asyncio
import logging

import wikipediaapi

logging.basicConfig(level=logging.INFO)

user_agent = "Wikipedia-API Example (merlin@example.com)"


def print_sections(sections, level=0):
    for s in sections:
        print("{}: {} - {}".format("*" * (level + 1), s.title, s.text[0:40]))
        print_sections(s.sections, level + 1)


async def print_langlinks(page):
    langlinks = await page.langlinks()
    for k in sorted(langlinks.keys()):
        v = langlinks[k]
        print(f"{k}: {v.language} - {v.title}: {v.fullurl}")


async def print_links(page):
    links = await page.links()
    for title in sorted(links.keys()):
        print(f"{title}: {links[title]}")


async def print_categories(page):
    categories = await page.categories()
    for title in sorted(categories.keys()):
        print(f"{title}: {categories[title]}")


async def print_categorymembers(categorymembers, level=0, max_level=2):
    for c in categorymembers.values():
        print("%s %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            await print_categorymembers(await c.categorymembers(), level + 1, max_level=max_level)


async def main():
    wiki_wiki = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="en")

    page_py = wiki_wiki.page("Python_(programming_language)")
    summary_py = await page_py.summary()

    print("Page - Exists: %s" % page_py.exists())
    print("Page - Id: %s" % page_py.pageid)
    print("Page - Title: %s" % page_py.title)
    print("Page - Summary: %s" % summary_py[0:60])

    print("Sections:")
    print_sections(page_py.sections)

    print("Lang links:")
    await print_langlinks(page_py)

    print("Links:")
    await print_links(page_py)

    print("Categories")
    await print_categories(page_py)

    section_py = page_py.section_by_title("Features and philosophy")
    if section_py is not None:
        print("Section - Title: %s" % section_py.title)
        print("Section - Text: %s" % section_py.text[0:60])
    else:
        print("Section does not exist.")

    wiki_html = wikipediaapi.AsyncWikipedia(
        user_agent=user_agent, language="cs", extract_format=wikipediaapi.ExtractFormat.HTML
    )

    page_ostrava = wiki_html.page("Ostrava")
    summary_ostrava = await page_ostrava.summary()

    print("Page - Exists: %s" % page_ostrava.exists())
    print("Page - Id: %s" % page_ostrava.pageid)
    print("Page - Title: %s" % page_ostrava.title)
    print("Page - Summary: %s" % summary_ostrava[0:60])
    print_sections(page_ostrava.sections)

    section_ostrava = page_ostrava.section_by_title("Heraldický znak")
    if section_ostrava is not None:
        print("Section - Title: %s" % section_ostrava.title)
        print("Section - Text: %s" % section_ostrava.text[0:60])
    else:
        print("Section does not exists")

    page_nonexisting = wiki_wiki.page("Wikipedia-API-FooBar")
    summary_nonexisting = await page_nonexisting.summary()

    print("Page - Exists: %s" % page_nonexisting.exists())
    print("Page - Id: %s" % page_nonexisting.pageid)
    print("Page - Title: %s" % page_nonexisting.title)
    print("Page - Summary: %s" % summary_nonexisting[0:60])

    wiki_de = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="de")
    de_page = wiki_de.page("Deutsche Sprache")
    await de_page.summary()
    print(de_page.title + ": " + de_page.fullurl)

    langlinks = await de_page.langlinks()
    en_page = langlinks["en"]
    print(en_page.title + ": " + en_page.fullurl)
    print((await en_page.summary())[0:60])

    cat = wiki_wiki.page("Category:Physics")
    print("Category members: Category:Physics")
    await print_categorymembers(await cat.categorymembers(), max_level=1)

    wiki_hi = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="hi")
    # fetch page about Python in Hindu
    # https://hi.wikipedia.org/wiki/%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8

    p_hi_python_quoted = wiki_hi.article(
        title="%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
        unquote=True,
    )
    print(p_hi_python_quoted.title)
    print((await p_hi_python_quoted.summary())[0:60])

    # Fetch page about Python in Chinese
    wiki_zh = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="zh")
    zh_page = wiki_zh.page("Python")
    await zh_page.summary()
    print(zh_page.title + ": " + zh_page.fullurl)
    print(repr(zh_page.varianttitles))

    # https://zh.wikipedia.org/zh-cn/Python
    wiki_zh_cn = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="zh", variant="zh-cn")
    zh_page_cn = wiki_zh_cn.page("Python")
    await zh_page_cn.summary()
    print(zh_page_cn.title + ": " + zh_page_cn.fullurl)
    print(repr(zh_page_cn.varianttitles))

    # https://zh.wikipedia.org/zh-tw/Python
    wiki_zh_tw = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="zh", variant="zh-tw")
    zh_page_tw = wiki_zh_tw.page("Python")
    await zh_page_tw.summary()
    print(zh_page_tw.title + ": " + zh_page_tw.fullurl)
    print(repr(zh_page_tw.varianttitles))

    # https://zh.wikipedia.org/zh-sg/Python
    wiki_zh_sg = wikipediaapi.AsyncWikipedia(user_agent=user_agent, language="zh", variant="zh-sg")
    zh_page_sg = wiki_zh_sg.page("Python")
    await zh_page_sg.summary()
    print(zh_page_sg.title + ": " + zh_page_sg.fullurl)
    print(repr(zh_page_sg.varianttitles))


asyncio.run(main())
