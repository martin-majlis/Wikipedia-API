import logging

from wikipedia import wikipedia
logging.basicConfig(level=logging.INFO)

wiki = wikipedia.Wikipedia('en')

page = wiki.article('Python_(programming_language)')
print(repr(page))

structured = page.structured()
print(repr(structured))

print(repr(page))
