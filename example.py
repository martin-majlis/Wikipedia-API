import logging

import wikipediaapi

logging.basicConfig(level=logging.INFO)

wiki_wiki = wikipediaapi.Wikipedia('en')

page_py = wiki_wiki.page('Python_(programming_language)')

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
        print("%s: %s - %s: %s" % (k, v.lang, v.title, v.url))


print("Lang links:")
print_langlinks(page_py)


def print_links(page):
    links = page.links
    for title in sorted(links.keys()):
        print("%s: %s" % (title, links[title]))


print("Links:")
print_links(page_py)

section_py = page_py.section_by_title('Features and philosophy')
print("Section - Title: %s" % section_py.title)
print("Section - Text: %s" % section_py.text[0:60])


wiki_html = wikipediaapi.Wikipedia(
    language='cs',
    extract_format=wikipediaapi.ExtractFormat.HTML
)

page_ostrava = wiki_html.page('Ostrava')
print("Page - Exists: %s" % page_ostrava.exists())
print("Page - Id: %s" % page_ostrava.pageid)
print("Page - Title: %s" % page_ostrava.title)
print("Page - Summary: %s" % page_ostrava.summary[0:60])
print_sections(page_ostrava.sections)

section_ostrava = page_ostrava.section_by_title('Heraldický znak')
print("Section - Title: %s" % section_ostrava.title)
print("Section - Text: %s" % section_ostrava.text[0:60])

page_nonexisting = wiki_wiki.page('Wikipedia-API-FooBar')
print("Page - Exists: %s" % page_nonexisting.exists())
print("Page - Id: %s" % page_nonexisting.pageid)
print("Page - Title: %s" % page_nonexisting.title)
print("Page - Summary: %s" % page_nonexisting.summary[0:60])
