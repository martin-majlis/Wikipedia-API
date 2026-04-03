#!/usr/bin/env python3
# Skill: multilingual_content
# Goal: Read the same Wikipedia topic across multiple languages.
# Steps: fetch English page → get langlinks → re-read summary in target languages

import wikipediaapi

USER_AGENT = "WikipediaAPI-Skills/1.0 (multilingual_content sync)"
TOPIC = "Artificial intelligence"
TARGET_LANGS = ["de", "fr", "ja", "es"]

wiki_en = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="en")
page = wiki_en.page(TOPIC)

if not page.exists():
    print(f"Page '{TOPIC}' not found.")
    raise SystemExit(1)

# 1. English summary
print(f"=== English: {page.title} ===")
print(page.summary[:400])
print()

# 2. Language links
langlinks = page.langlinks
print(f"Available language links: {len(langlinks)} languages")
available = sorted(langlinks.keys())
print(f"  {', '.join(available[:20])}{'...' if len(available) > 20 else ''}\n")

# 3. Re-fetch summary in each target language
for lang in TARGET_LANGS:
    if lang not in langlinks:
        print(f"=== {lang.upper()}: not available ===\n")
        continue

    lp = langlinks[lang]
    wiki_lang = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language=lang)
    foreign_page = wiki_lang.page(lp.title)

    print(f"=== {lang.upper()}: {foreign_page.title} ===")
    summary = foreign_page.summary
    print(summary[:400] if summary else "(no summary)")
    print()
