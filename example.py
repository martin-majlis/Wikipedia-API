import logging

import wikipedia

logging.basicConfig(level=logging.INFO)

wiki = wikipedia.Wikipedia('en')

page = wiki.article('Python_(programming_language)')

print("Page - Id: %s" % page.id())
print("Page - Title: %s" % page.title())
print("Page - Summary: %s" % page.summary())


def print_sections(sections, level=0):
    for s in sections:
        print("%s: %s - %s" % ("*" * (level + 1), s.title(), s.text()[0:40]))
        print_sections(s.sections(), level + 1)


print_sections(page.sections())

libraries = page.section_by_title('Libraries')
print("Section - Title: %s" % libraries.title())
print("Section - Text: %s" % libraries.text())
