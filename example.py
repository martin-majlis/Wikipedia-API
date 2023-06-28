# -*- coding: utf-8 -*-

import logging

import wikipediaapi

logging.basicConfig(level=logging.INFO)

user_agent = "Wikipedia-API Example (merlin@example.com)"

wiki_wiki = wikipediaapi.Wikipedia(user_agent, "en")

page_py = wiki_wiki.page("Python_(programming_language)")

print("Page - Exists: %s" % page_py.exists())
print("Page - Id: %s" % page_py.pageid)
print("Page - Title: %s" % page_py.title)
print("Page - Summary: %s" % page_py.summary[0:60])


def print_sections(sections, level=0):
    for s in sections:
        print("%s: %s - %s" % ("*" * (level + 1), s.title, s.text[0:40]))
        print_sections(s.sections, level + 1)


print("Sections:")
print_sections(page_py.sections)


def print_langlinks(page):
    langlinks = page.langlinks
    for k in sorted(langlinks.keys()):
        v = langlinks[k]
        print("%s: %s - %s: %s" % (k, v.language, v.title, v.fullurl))


print("Lang links:")
print_langlinks(page_py)


def print_links(page):
    links = page.links
    for title in sorted(links.keys()):
        print("%s: %s" % (title, links[title]))


print("Links:")
print_links(page_py)


def print_categories(page):
    categories = page.categories
    for title in sorted(categories.keys()):
        print("%s: %s" % (title, categories[title]))


print("Categories")
print_categories(page_py)

section_py = page_py.section_by_title("Features and philosophy")
if section_py is not None:
    print("Section - Title: %s" % section_py.title)
    print("Section - Text: %s" % section_py.text[0:60])
else:
    print("Section does not exist.")

wiki_html = wikipediaapi.Wikipedia(
    user_agent=user_agent, language="cs", extract_format=wikipediaapi.ExtractFormat.HTML
)

page_ostrava = wiki_html.page("Ostrava")
print("Page - Exists: %s" % page_ostrava.exists())
print("Page - Id: %s" % page_ostrava.pageid)
print("Page - Title: %s" % page_ostrava.title)
print("Page - Summary: %s" % page_ostrava.summary[0:60])
print_sections(page_ostrava.sections)

section_ostrava = page_ostrava.section_by_title("Heraldický znak")
if section_ostrava is not None:
    print("Section - Title: %s" % section_ostrava.title)
    print("Section - Text: %s" % section_ostrava.text[0:60])
else:
    print("Section does not exists")

page_nonexisting = wiki_wiki.page("Wikipedia-API-FooBar")
print("Page - Exists: %s" % page_nonexisting.exists())
print("Page - Id: %s" % page_nonexisting.pageid)
print("Page - Title: %s" % page_nonexisting.title)
print("Page - Summary: %s" % page_nonexisting.summary[0:60])


wiki_de = wikipediaapi.Wikipedia(user_agent, "de")
de_page = wiki_de.page("Deutsche Sprache")
print(de_page.title + ": " + de_page.fullurl)
print(de_page.summary[0:60])

en_page = de_page.langlinks["en"]
print(en_page.title + ": " + en_page.fullurl)
print(en_page.summary[0:60])


def print_categorymembers(categorymembers, level=0, max_level=2):
    for c in categorymembers.values():
        print("%s %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            print_categorymembers(c.categorymembers, level + 1, max_level=max_level)


cat = wiki_wiki.page("Category:Physics")
print("Category members: Category:Physics")
print_categorymembers(cat.categorymembers, max_level=1)

wiki_hi = wikipediaapi.Wikipedia(user_agent, "hi")
# fetch page about Python in Hindu
# https://hi.wikipedia.org/wiki/%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8

p_hi_python_quoted = wiki_hi.article(
    title="%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8",
    unquote=True,
)
print(p_hi_python_quoted.title)
print(p_hi_python_quoted.summary[0:60])
