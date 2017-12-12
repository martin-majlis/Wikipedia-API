import logging

import wikipedia

logging.basicConfig(level=logging.INFO)

wiki_wiki = wikipedia.Wikipedia('en')

page_py = wiki_wiki.article('Python_(programming_language)')

print("Page - Id: %s" % page_py.id())
print("Page - Title: %s" % page_py.title())
print("Page - Summary: %s" % page_py.summary()[0:60])


def print_sections(sections, level=0):
    for s in sections:
        print("%s: %s - %s" % ("*" * (level + 1), s.title(), s.text()[0:40]))
        print_sections(s.sections(), level + 1)


print_sections(page_py.sections())

section_py = page_py.section_by_title('Features and philosophy')
print("Section - Title: %s" % section_py.title())
print("Section - Text: %s" % section_py.text()[0:60])


wiki_html = wikipedia.Wikipedia(
    language='cs',
    extract_format=wikipedia.ExtractFormat.HTML
)

page_ostrava = wiki_html.article('Ostrava')
print("Page - Id: %s" % page_ostrava.id())
print("Page - Title: %s" % page_ostrava.title())
print("Page - Summary: %s" % page_ostrava.summary()[0:60])
print_sections(page_ostrava.sections())

section_ostrava = page_ostrava.section_by_title('Heraldický znak')
print("Section - Title: %s" % section_ostrava.title())
print("Section - Text: %s" % section_ostrava.text()[0:60])
