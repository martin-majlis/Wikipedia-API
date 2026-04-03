#!/usr/bin/env python3
# Skill: multilingual_content
# Goal: Read the same Wikipedia topic across multiple languages (async version).
# Steps: fetch English page → get langlinks → re-read summary in target languages

import asyncio

import wikipediaapi

USER_AGENT = "WikipediaAPI-Skills/1.0 (multilingual_content async)"
TOPIC = "Artificial intelligence"
TARGET_LANGS = ["de", "fr", "ja", "es"]


async def main():
    wiki_en = wikipediaapi.AsyncWikipedia(user_agent=USER_AGENT, language="en")
    page = wiki_en.page(TOPIC)

    if not await page.exists():
        print(f"Page '{TOPIC}' not found.")
        return

    # 1. English summary
    print(f"=== English: {page.title} ===")
    print((await page.summary)[:400])
    print()

    # 2. Language links
    langlinks = await page.langlinks
    print(f"Available language links: {len(langlinks)} languages")
    available = sorted(langlinks.keys())
    print(f"  {', '.join(available[:20])}{'...' if len(available) > 20 else ''}\n")

    # 3. Re-fetch summary in each target language (concurrent)
    async def fetch_lang(lang: str) -> tuple[str, str, str]:
        if lang not in langlinks:
            return lang, "", "(not available)"
        lp = langlinks[lang]
        wiki_lang = wikipediaapi.AsyncWikipedia(user_agent=USER_AGENT, language=lang)
        foreign_page = wiki_lang.page(lp.title)
        summary = await foreign_page.summary
        return lang, foreign_page.title, summary[:400] if summary else "(no summary)"

    summaries = await asyncio.gather(*[fetch_lang(lang) for lang in TARGET_LANGS])

    for lang, title, text in summaries:
        print(f"=== {lang.upper()}: {title} ===")
        print(text)
        print()


asyncio.run(main())
