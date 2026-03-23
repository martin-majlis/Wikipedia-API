# flake8: noqa

user_agent = "UnitTests (bot@example.com)"


def wikipedia_api_request(wiki):
    def api_request(language, params):
        query = ""
        for k in sorted(params.keys()):
            query += k + "=" + str(params[k]) + "&"

        return _MOCK_DATA[language + ":" + query]

    return api_request


def async_wikipedia_api_request(wiki):
    async def api_request(language, params):
        query = ""
        for k in sorted(params.keys()):
            query += k + "=" + str(params[k]) + "&"

        return _MOCK_DATA[language + ":" + query]

    return api_request


_MOCK_DATA = {
    "en:action=query&explaintext=1&exsectionformat=wiki&format=json&prop=extracts&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "warnings": {
            "extracts": {
                "*": '"exlimit" was too large for a whole article extracts request, lowered to 1.'
            }
        },
        "query": {
            "normalized": [{"from": "Test_1", "to": "Test 1"}],
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "extract": (
                        "Summary text\n\n\n"
                        + "== Section 1 ==\n"
                        + "Text for section 1\n\n\n"
                        + "=== Section 1.1 ===\n"
                        + "Text for section 1.1\n\n\n"
                        + "=== Section 1.2 ===\n"
                        + "Text for section 1.2\n\n\n"
                        + "== Section 2 ==\n"
                        + "Text for section 2\n\n\n"
                        + "== Section 3 ==\n"
                        + "Text for section 3\n\n\n"
                        + "== Section 4 ==\n\n\n"
                        + "=== Section 4.1 ===\n"
                        + "Text for section 4.1\n\n\n"
                        + "=== Section 4.2 ===\n"
                        + "Text for section 4.2\n\n\n"
                        + "==== Section 4.2.1 ====\n"
                        + "Text for section 4.2.1\n\n\n"
                        + "==== Section 4.2.2 ====\n"
                        + "Text for section 4.2.2\n\n\n"
                        + "== Section 5 ==\n"
                        + "Text for section 5\n\n\n"
                        + "=== Section 5.1 ===\n"
                        + "Text for section 5.1\n"
                    ),
                }
            },
        },
    },
    "en:action=query&explaintext=1&exsectionformat=wiki&format=json&prop=extracts&redirects=1&titles=No_Sections&": {
        "batchcomplete": "",
        "warnings": {
            "extracts": {
                "*": '"exlimit" was too large for a whole article extracts request, lowered to 1.'
            }
        },
        "query": {
            "normalized": [{"from": "No_Sections", "to": "No Sections"}],
            "pages": {
                "4": {
                    "pageid": 5,
                    "ns": 0,
                    "title": "No Sections",
                    "extract": ("Summary text\n\n\n"),
                }
            },
        },
    },
    "en:action=query&format=json&prop=extracts&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "warnings": {
            "extracts": {
                "*": '"exlimit" was too large for a whole article extracts request, lowered to 1.'
            }
        },
        "query": {
            "normalized": [{"from": "Test_1", "to": "Test 1"}],
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "extract": (
                        "<p><b>Summary</b> text\n\n</p>\n"
                        + "<h2>Section 1</h2>\n"
                        + "<p>Text for section 1</p>\n\n\n"
                        + '<h3><span id="s1.1">Section 1.1</span></h3>\n'
                        + "<p><b>Text for section 1.1</b>\n\n\n</p>"
                        + "<h3>Section 1.2</h3>\n"
                        + "<p><b>Text for section 1.2</b>\n\n\n</p>"
                        + '<h2><span id="s2">Section 2</span></h2>\n'
                        + "<p><b>Text for section 2</b>\n\n\n</p>"
                        + "<h2><span id='s3'>Section 3</span></h2>\n"
                        + "<p><b>Text for section 3</b>\n\n\n</p>"
                        + '<h2 id="s4">Section 4</h2>\n'
                        + '<h3><span id="s4.1">Section 4.1</span></h3>\n'
                        + "<p><b>Text for section 4.1</b>\n\n\n</p>"
                        + '<h3><span id="s4.2">Section 4.2</span></h3>\n'
                        + "<p><b>Text for section 4.2</b>\n\n\n</p>"
                        + '<h4><span id="s4.2.1">Section 4.2.1</span></h4>\n'
                        + "<p><b>Text for section 4.2.1</b>\n\n\n</p>"
                        + '<h4><span id="s4.2.2">Section 4.2.2</span></h4>\n'
                        + "<p><b>Text for section 4.2.2</b>\n\n\n</p>"
                        + '<h2><span id="s5a"></span><span id="s5b">Section 5</span></h2>\n'
                        + "<p><b>Text for section 5</b>\n\n\n</p>"
                        + '<h3><span id="s5.1">Section 5.1</span></h3>\n'
                        + "<p>Text for section 5.1\n\n\n</p>"
                    ),
                }
            },
        },
    },
    "en:action=query&format=json&prop=extracts&redirects=1&titles=Test_Nested&": {
        "batchcomplete": "",
        "warnings": {
            "extracts": {
                "*": '"exlimit" was too large for a whole article extracts request, lowered to 1.'
            }
        },
        "query": {
            "normalized": [{"from": "Test_Nested", "to": "Test Nested"}],
            "pages": {
                "4": {
                    "pageid": 14,
                    "ns": 0,
                    "title": "Test Nested",
                    "extract": (
                        "<p><b>Summary</b> text\n\n</p>\n"
                        + "<h2>Section 1</h2>\n"
                        + "<p>Text for section 1</p>\n\n\n"
                        + '<h3><span id="s1.1">Subsection A</span></h3>\n'
                        + "<p><b>Text for section 1.A</b>\n\n\n</p>"
                        + "<h3>Subsection B</h3>\n"
                        + "<p><b>Text for section 1.B</b>\n\n\n</p>"
                        + '<h2><span id="s2">Section 2</span></h2>\n'
                        + "<p><b>Text for section 2</b>\n\n\n</p>"
                        + '<h3><span id="s2.1">Subsection A</span></h3>\n'
                        + "<p><b>Text for section 2.A</b>\n\n\n</p>"
                        + "<h3>Subsection B</h3>\n"
                        + "<p><b>Text for section 2.B</b>\n\n\n</p>"
                        + "<h2><span id='s3'>Section 3</span></h2>\n"
                        + "<p><b>Text for section 3</b>\n\n\n</p>"
                        + '<h3><span id="s3.1">Subsection A</span></h3>\n'
                        + "<p><b>Text for section 3.A</b>\n\n\n</p>"
                        + "<h3>Subsection B</h3>\n"
                        + "<p><b>Text for section 3.B</b>\n\n\n</p>"
                    ),
                }
            },
        },
    },
    "en:action=query&format=json&prop=extracts&redirects=1&titles=Test_Edit&": {
        "batchcomplete": "",
        "warnings": {
            "extracts": {
                "*": '"exlimit" was too large for a whole article extracts request, lowered to 1.'
            }
        },
        "query": {
            "normalized": [{"from": "Test_Edit", "to": "Test Edit"}],
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test Edit",
                    "extract": (
                        "<p><b>Summary</b> text\n\n</p>\n"
                        + "<h2>Section 1</h2>\n"
                        + "<p>Text for section 1</p>\n\n\n"
                        + '<h3><span id="s1.Edit">Section with Edit</span><span>Edit</span></h3>\n'
                        + "<p>Text for section with edit\n\n\n</p>"
                    ),
                }
            },
        },
    },
    "en:action=query&format=json&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle|varianttitles&prop=info&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "query": {
            "normalized": [{"from": "Test_1", "to": "Test 1"}],
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "missing": "",
                    "contentmodel": "wikitext",
                    "pagelanguage": "en",
                    "pagelanguagehtmlcode": "en",
                    "pagelanguagedir": "ltr",
                    "touched": "2023-01-01T00:00:00Z",
                    "lastrevid": 12345,
                    "length": 6789,
                    "protection": [{"type": "create", "level": "sysop", "expiry": "infinity"}],
                    "restrictiontypes": ["create"],
                    "watchers": 100,
                    "visitingwatchers": 50,
                    "notificationtimestamp": "",
                    "talkid": 5,
                    "fullurl": "https://en.wikipedia.org/wiki/Test_1",
                    "editurl": "https://en.wikipedia.org/w/index.php?title=Test_1&action=edit",
                    "canonicalurl": "https://en.wikipedia.org/wiki/Test_1",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "Test 1",
                    "varianttitles": {},
                    "api_new_experimental_field": "test_value",
                }
            },
        },
    },
    "l1:action=query&format=json&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle|varianttitles&prop=info&redirects=1&titles=Test 1 - 1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "10": {
                    "pageid": 10,
                    "ns": 0,
                    "title": "Test 1 - 1",
                    "missing": "",
                    "contentmodel": "wikitext",
                    "pagelanguage": "l1",
                    "pagelanguagehtmlcode": "l1",
                    "pagelanguagedir": "ltr",
                    "protection": [{"type": "create", "level": "sysop", "expiry": "infinity"}],
                    "restrictiontypes": ["create"],
                    "notificationtimestamp": "",
                    "fullurl": "https://l1.wikipedia.org/wiki/Test 1 - 1",
                    "editurl": "https://l1.wikipedia.org/w/index.php?title=Test 1 - 1&action=edit",
                    "canonicalurl": "https://l1.wikipedia.org/wiki/Test 1 - 1",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "Test 1 - 1",
                }
            }
        },
    },
    "en:action=query&format=json&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle|varianttitles&prop=info&redirects=1&titles=NonExisting&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "-1": {
                    "ns": 0,
                    "title": "NonExisting",
                    "missing": "",
                    "contentmodel": "wikitext",
                    "pagelanguage": "en",
                    "pagelanguagehtmlcode": "en",
                    "pagelanguagedir": "ltr",
                    "protection": [],
                    "restrictiontypes": ["create"],
                    "notificationtimestamp": "",
                    "fullurl": "https://en.wikipedia.org/wiki/NonExisting",
                    "editurl": "https://en.wikipedia.org/w/index.php?title=NonExisting&action=edit",
                    "canonicalurl": "https://en.wikipedia.org/wiki/NonExisting",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "NonExisting",
                }
            }
        },
    },
    "en:action=query&format=json&lllimit=500&llprop=url&prop=langlinks&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "langlinks": [
                        {
                            "lang": "l1",
                            "url": "https://l1.wikipedia.org/wiki/Test_1_-_1",
                            "*": "Test 1 - 1",
                        },
                        {
                            "lang": "l2",
                            "url": "https://l2.wikipedia.org/wiki/Test_1_-_2",
                            "*": "Test 1 - 2",
                        },
                        {
                            "lang": "l3",
                            "url": "https://l3.wikipedia.org/wiki/Test_1_-_3",
                            "*": "Test 1 - 3",
                        },
                    ],
                }
            }
        },
    },
    "en:action=query&format=json&lllimit=500&llprop=url&prop=langlinks&redirects=1&titles=No_LangLinks&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "10": {
                    "pageid": 10,
                    "ns": 0,
                    "title": "No LangLinks",
                }
            }
        },
    },
    "en:action=query&format=json&pllimit=500&prop=links&redirects=1&titles=Test_1&": {
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "links": [
                        {"ns": 0, "title": "Title - 1"},
                        {"ns": 0, "title": "Title - 2"},
                        {"ns": 0, "title": "Title - 3"},
                    ],
                }
            }
        }
    },
    "en:action=query&format=json&pllimit=500&prop=links&redirects=1&titles=Test_2&": {
        "continue": {"plcontinue": "5|0|Title_-_4", "continue": "||"},
        "query": {
            "pages": {
                "4": {
                    "pageid": 5,
                    "ns": 0,
                    "title": "Test 2",
                    "links": [
                        {"ns": 0, "title": "Title - 1"},
                        {"ns": 0, "title": "Title - 2"},
                        {"ns": 0, "title": "Title - 3"},
                    ],
                }
            }
        },
    },
    "en:action=query&format=json&plcontinue=5|0|Title_-_4&pllimit=500&prop=links&redirects=1&titles=Test_2&": {
        "query": {
            "pages": {
                "4": {
                    "pageid": 5,
                    "ns": 0,
                    "title": "Test 2",
                    "links": [
                        {"ns": 0, "title": "Title - 4"},
                        {"ns": 0, "title": "Title - 5"},
                    ],
                }
            }
        }
    },
    "en:action=query&format=json&pllimit=500&prop=links&redirects=1&titles=No_Links&": {
        "query": {
            "pages": {
                "4": {
                    "pageid": 11,
                    "ns": 0,
                    "title": "No_Links",
                }
            }
        }
    },
    "en:action=query&cllimit=500&format=json&prop=categories&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "categories": [
                        {"ns": 14, "title": "Category:C1"},
                        {"ns": 14, "title": "Category:C2"},
                        {"ns": 14, "title": "Category:C3"},
                    ],
                }
            }
        },
    },
    "en:action=query&cmlimit=500&cmtitle=Category:C1&format=json&list=categorymembers&redirects=1&": {
        "query": {
            "categorymembers": [
                {"ns": 0, "pageid": 4, "title": "Title - 1"},
                {"ns": 0, "pageid": 5, "title": "Title - 2"},
                {"ns": 0, "pageid": 6, "title": "Title - 3"},
            ]
        }
    },
    "en:action=query&cmlimit=500&cmtitle=Category:C2&format=json&list=categorymembers&redirects=1&": {
        "continue": {"cmcontinue": "5|0|Title_-_4", "continue": "-||"},
        "query": {
            "categorymembers": [
                {"ns": 0, "pageid": 4, "title": "Title - 1"},
                {"ns": 0, "pageid": 5, "title": "Title - 2"},
                {"ns": 0, "pageid": 6, "title": "Title - 3"},
            ]
        },
    },
    "en:action=query&cmcontinue=5|0|Title_-_4&cmlimit=500&cmtitle=Category:C2&format=json&list=categorymembers&redirects=1&": {
        "query": {
            "categorymembers": [
                {"ns": 0, "pageid": 7, "title": "Title - 4"},
                {"ns": 0, "pageid": 8, "title": "Title - 5"},
            ]
        }
    },
    "en:action=query&cllimit=500&format=json&prop=categories&redirects=1&titles=No_Categories&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                }
            }
        },
    },
    "en:action=query&bllimit=500&bltitle=Non_Existent&format=json&list=backlinks&redirects=1&": {
        "query": {"backlinks": []}
    },
    "en:action=query&bllimit=500&bltitle=Test_1&format=json&list=backlinks&redirects=1&": {
        "query": {
            "backlinks": [
                {"ns": 0, "title": "Title - 1"},
                {"ns": 0, "title": "Title - 2"},
                {"ns": 0, "title": "Title - 3"},
            ]
        }
    },
    "en:action=query&bllimit=500&bltitle=Test_2&format=json&list=backlinks&redirects=1&": {
        "continue": {"blcontinue": "5|0|Title_-_4", "continue": "||"},
        "query": {
            "backlinks": [
                {"ns": 0, "title": "Title - 1"},
                {"ns": 0, "title": "Title - 2"},
                {"ns": 0, "title": "Title - 3"},
            ]
        },
    },
    "en:action=query&blcontinue=5|0|Title_-_4&bllimit=500&bltitle=Test_2&format=json&list=backlinks&redirects=1&": {
        "query": {
            "backlinks": [
                {"ns": 0, "title": "Title - 4"},
                {"ns": 0, "title": "Title - 5"},
            ]
        }
    },
    "hi:action=query&format=json&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle|varianttitles&prop=info&redirects=1&titles=पाइथन&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "10": {
                    "pageid": 10,
                    "ns": 0,
                    "title": "पाइथन",
                    "missing": "",
                    "contentmodel": "wikitext",
                    "pagelanguage": "hi",
                    "pagelanguagehtmlcode": "hi",
                    "pagelanguagedir": "ltr",
                    "protection": [{"type": "create", "level": "sysop", "expiry": "infinity"}],
                    "restrictiontypes": ["create"],
                    "notificationtimestamp": "",
                    "fullurl": "https://l1.wikipedia.org/wiki/Test 1 - 1",
                    "editurl": "https://l1.wikipedia.org/w/index.php?title=Test 1 - 1&action=edit",
                    "canonicalurl": "https://l1.wikipedia.org/wiki/Test 1 - 1",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "पाइथन",
                }
            }
        },
    },
    "zh:action=query&explaintext=1&exsectionformat=wiki&format=json&prop=extracts&redirects=1&titles=Test_Zh-Tw&variant=zh-tw&": {
        "batchcomplete": "",
        "warnings": {
            "extracts": {
                "*": '"exlimit" was too large for a whole article extracts request, lowered to 1.'
            }
        },
        "query": {
            "normalized": [{"from": "Test_Zh-Tw", "to": "Test Zh-Tw"}],
            "pages": {
                "4": {
                    "pageid": 44,
                    "ns": 0,
                    "title": "Test Zh-Tw",
                    "extract": ("ZH-TW\n\n\n"),
                }
            },
        },
    },
    "zh:action=query&format=json&pllimit=500&prop=links&redirects=1&titles=Test_Zh-Tw&variant=zh-tw&": {
        "query": {
            "pages": {
                "44": {
                    "pageid": 44,
                    "ns": 0,
                    "title": "Test Zh-Tw",
                    "links": [
                        {"ns": 0, "title": "Title - Zh-Tw - 1"},
                        {"ns": 0, "title": "Title - Zh-Tw - 2"},
                        {"ns": 0, "title": "Title - Zh-Tw - 3"},
                    ],
                }
            }
        }
    },
    "zh:action=query&format=json&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle|varianttitles&prop=info&redirects=1&titles=Test_Zh-Tw&variant=zh-tw&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "44": {
                    "pageid": 44,
                    "ns": 0,
                    "title": "Test Zh-Tw",
                    "missing": "",
                    "contentmodel": "wikitext",
                    "pagelanguage": "zh",
                    "pagelanguagehtmlcode": "zh",
                    "pagelanguagedir": "ltr",
                    "protection": [{"type": "create", "level": "sysop", "expiry": "infinity"}],
                    "restrictiontypes": ["create"],
                    "notificationtimestamp": "",
                    "fullurl": "https://zh.wikipedia.org/wiki/Test Zh-Tw",
                    "editurl": "https://zh.wikipedia.org/w/index.php?title=Test Zh-Tw&action=edit",
                    "canonicalurl": "https://zh.wikipedia.org/wiki/Test Zh-Tw",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "Test Zh-Tw",
                    "varianttitles": {
                        "zh": "Test Zh",
                        "zh-hans": "Test Zh-Hans",
                        "zh-tw": "Test Zh-Tw",
                    },
                }
            }
        },
    },
    "en:action=query&foo=bar&format=json&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle|varianttitles&prop=info&redirects=1&titles=Extra_API_Params&": {
        "batchcomplete": "",
        "query": {
            "normalized": [{"from": "Extra_API_Params", "to": "Extra API Params"}],
            "pages": {
                "4": {
                    "pageid": 9,
                    "ns": 0,
                    "title": "Extra API Params",
                    "missing": "",
                    "contentmodel": "wikitext",
                    "pagelanguage": "en",
                    "pagelanguagehtmlcode": "en",
                    "pagelanguagedir": "ltr",
                    "protection": [{"type": "create", "level": "sysop", "expiry": "infinity"}],
                    "restrictiontypes": ["create"],
                    "notificationtimestamp": "",
                    "fullurl": "https://en.wikipedia.org/wiki/Extra_API_Params",
                    "editurl": "https://en.wikipedia.org/w/index.php?title=Extra_API_Params&action=edit",
                    "canonicalurl": "https://en.wikipedia.org/wiki/Extra_API_Params",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "Extra API Params",
                }
            },
        },
    },
    # ── coordinates (prop=coordinates) ──────────────────────────────────────────
    "en:action=query&colimit=10&coprimary=primary&coprop=globe&format=json&prop=coordinates&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "coordinates": [
                        {
                            "lat": 51.5074,
                            "lon": -0.1278,
                            "primary": "",
                            "globe": "earth",
                        }
                    ],
                }
            }
        },
    },
    "en:action=query&colimit=10&coprimary=all&coprop=globe&format=json&prop=coordinates&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "coordinates": [
                        {
                            "lat": 51.5074,
                            "lon": -0.1278,
                            "primary": "",
                            "globe": "earth",
                        },
                        {
                            "lat": 48.8566,
                            "lon": 2.3522,
                            "globe": "earth",
                        },
                    ],
                }
            }
        },
    },
    "en:action=query&colimit=10&coprimary=primary&coprop=globe&format=json&prop=coordinates&redirects=1&titles=NonExistent&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "-1": {
                    "ns": 0,
                    "title": "NonExistent",
                    "missing": "",
                }
            }
        },
    },
    # ── images (prop=images) ────────────────────────────────────────────────────
    "en:action=query&format=json&imdir=ascending&imlimit=10&prop=images&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "images": [
                        {"ns": 6, "title": "File:Example.png"},
                        {"ns": 6, "title": "File:Logo.svg"},
                    ],
                }
            }
        },
    },
    "en:action=query&format=json&imdir=ascending&imlimit=10&prop=images&redirects=1&titles=NonExistent&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "-1": {
                    "ns": 0,
                    "title": "NonExistent",
                    "missing": "",
                }
            }
        },
    },
    # ── coordinates with normalized title (for CLI tests) ──────────────────────
    "en:action=query&colimit=10&coprimary=primary&coprop=globe&format=json&prop=coordinates&redirects=1&titles=Test 1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "coordinates": [
                        {
                            "lat": 51.5074,
                            "lon": -0.1278,
                            "primary": "",
                            "globe": "earth",
                        }
                    ],
                }
            }
        },
    },
    # ── images with normalized title (for CLI tests) ─────────────────────────
    "en:action=query&format=json&imdir=ascending&imlimit=10&prop=images&redirects=1&titles=Test 1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "images": [
                        {"ns": 6, "title": "File:Example.png"},
                        {"ns": 6, "title": "File:Logo.svg"},
                    ],
                }
            }
        },
    },
    # ── geosearch (list=geosearch) ──────────────────────────────────────────────
    "en:action=query&format=json&gscoord=51.5074|-0.1278&gsglobe=earth&gslimit=10&gsradius=500&gssort=distance&list=geosearch&redirects=1&": {
        "batchcomplete": "",
        "query": {
            "geosearch": [
                {
                    "pageid": 100,
                    "ns": 0,
                    "title": "Nearby Page 1",
                    "lat": 51.508,
                    "lon": -0.128,
                    "dist": 50.3,
                    "primary": "",
                },
                {
                    "pageid": 101,
                    "ns": 0,
                    "title": "Nearby Page 2",
                    "lat": 51.510,
                    "lon": -0.130,
                    "dist": 200.7,
                    "primary": "",
                },
            ]
        },
    },
    # ── random (list=random) ────────────────────────────────────────────────────
    "en:action=query&format=json&list=random&redirects=1&rnfilterredir=nonredirects&rnlimit=2&": {
        "batchcomplete": "",
        "query": {
            "random": [
                {"id": 200, "ns": 0, "title": "Random Page A"},
                {"id": 201, "ns": 0, "title": "Random Page B"},
            ]
        },
    },
    # ── random with namespace (for CLI tests) ──────────────────────────────────
    "en:action=query&format=json&list=random&redirects=1&rnfilterredir=nonredirects&rnlimit=2&rnnamespace=0&": {
        "batchcomplete": "",
        "query": {
            "random": [
                {"id": 200, "ns": 0, "title": "Random Page A"},
                {"id": 201, "ns": 0, "title": "Random Page B"},
            ]
        },
    },
    "en:action=query&format=json&list=random&redirects=1&rnfilterredir=nonredirects&rnlimit=1&rnnamespace=0&": {
        "batchcomplete": "",
        "query": {
            "random": [
                {"id": 200, "ns": 0, "title": "Random Page A"},
            ]
        },
    },
    # ── batch coordinates (multi-title) ──────────────────────────────────────────
    "en:action=query&colimit=10&coprimary=primary&coprop=globe&format=json&prop=coordinates&redirects=1&titles=Test_1|NonExistent&": {
        "batchcomplete": "",
        "query": {
            "normalized": [{"from": "Test_1", "to": "Test 1"}],
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "coordinates": [
                        {
                            "lat": 51.5074,
                            "lon": -0.1278,
                            "primary": "",
                            "globe": "earth",
                        }
                    ],
                },
                "-1": {
                    "ns": 0,
                    "title": "NonExistent",
                    "missing": "",
                },
            },
        },
    },
    # ── batch images (multi-title) ─────────────────────────────────────────────
    "en:action=query&format=json&imdir=ascending&imlimit=10&prop=images&redirects=1&titles=Test_1|NonExistent&": {
        "batchcomplete": "",
        "query": {
            "normalized": [{"from": "Test_1", "to": "Test 1"}],
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "images": [
                        {"ns": 6, "title": "File:Example.png"},
                        {"ns": 6, "title": "File:Logo.svg"},
                    ],
                },
                "-1": {
                    "ns": 0,
                    "title": "NonExistent",
                    "missing": "",
                },
            },
        },
    },
    # ── search (list=search) ────────────────────────────────────────────────────
    "en:action=query&format=json&list=search&redirects=1&srlimit=10&srnamespace=0&srsearch=Python&srsort=relevance&": {
        "batchcomplete": "",
        "query": {
            "searchinfo": {"totalhits": 5432, "suggestion": "python programming"},
            "search": [
                {
                    "ns": 0,
                    "title": "Python (programming language)",
                    "pageid": 300,
                    "size": 123456,
                    "wordcount": 15000,
                    "snippet": '<span class="searchmatch">Python</span> is a programming language',
                    "timestamp": "2024-01-01T00:00:00Z",
                },
                {
                    "ns": 0,
                    "title": "Python (mythology)",
                    "pageid": 301,
                    "size": 5678,
                    "wordcount": 800,
                    "snippet": '<span class="searchmatch">Python</span> is a creature',
                    "timestamp": "2024-02-01T00:00:00Z",
                },
            ],
        },
    },
}


# ── CLI-specific mock data and helpers ───────────────────────────────────────────


def create_mock_wikipedia(language="en", variant=None, extract_format="wiki"):
    """Create a mock Wikipedia instance for testing CLI functions."""
    import wikipediaapi

    wiki = wikipediaapi.Wikipedia(
        user_agent=user_agent,
        language=language,
        variant=variant,
        extract_format=(
            wikipediaapi.ExtractFormat.WIKI
            if extract_format == "wiki"
            else wikipediaapi.ExtractFormat.HTML
        ),
    )
    wiki._get = wikipedia_api_request(wiki)
    return wiki


def create_mock_page(title, pageid=1, exists=True, language="en", namespace=0):
    """Create a mock Wikipedia page for testing."""
    import wikipediaapi

    wiki = create_mock_wikipedia(language)
    page = wikipediaapi.WikipediaPage(
        wiki=wiki,
        title=title,
        ns=wikipediaapi.Namespace.MAIN if namespace == 0 else wikipediaapi.Namespace.CATEGORY,
        language=language,
    )

    if exists:
        # Set up mock attributes for existing pages
        page._attributes = {
            "fullurl": f"https://{language}.wikipedia.org/wiki/{title}",
            "canonicalurl": f"https://{language}.wikipedia.org/wiki/{title}",
            "displaytitle": title,
            "pageid": pageid,
        }
    else:
        # Mock non-existent page
        page._attributes = {"missing": ""}

    return page


# CLI-specific mock responses for different scenarios
CLI_MOCK_PAGES = {
    "summary_test": {
        "title": "Test Page",
        "summary": "This is a test summary for the Wikipedia page.",
        "exists": True,
    },
    "text_test": {
        "title": "Test Page",
        "text": "This is the full text of the test page.\n\n== Section 1 ==\nContent for section 1.",
        "exists": True,
    },
    "sections_test": {
        "title": "Test Page",
        "sections": [
            {"title": "Introduction", "level": 1, "indent": 0},
            {"title": "History", "level": 1, "indent": 0},
            {"title": "Early History", "level": 2, "indent": 1},
            {"title": "Modern History", "level": 2, "indent": 1},
            {"title": "Geography", "level": 1, "indent": 0},
        ],
        "exists": True,
    },
    "links_test": {
        "title": "Test Page",
        "links": {
            "Related Page 1": create_mock_page("Related Page 1", 2, True),
            "Related Page 2": create_mock_page("Related Page 2", 3, True),
            "Related Page 3": create_mock_page("Related Page 3", 4, True),
        },
        "exists": True,
    },
    "langlinks_test": {
        "title": "Test Page",
        "langlinks": {
            "de": create_mock_page("Test Seite", 5, True, "de"),
            "fr": create_mock_page("Page de test", 6, True, "fr"),
            "es": create_mock_page("Página de prueba", 7, True, "es"),
        },
        "exists": True,
    },
    "categories_test": {
        "title": "Test Page",
        "categories": {
            "Category:Test": create_mock_page("Category:Test", 8, True),
            "Category:Example": create_mock_page("Category:Example", 9, True),
        },
        "exists": True,
    },
    "categorymembers_test": {
        "title": "Category:Test",
        "members": [
            {"title": "Test Page 1", "ns": 0, "level": 0},
            {"title": "Test Page 2", "ns": 0, "level": 0},
            {"title": "Subcategory", "ns": 14, "level": 0},
            {"title": "Subcategory Page", "ns": 0, "level": 1},
        ],
        "exists": True,
    },
    "nonexistent": {
        "title": "Nonexistent Page",
        "exists": False,
    },
}


# Additional mock API responses for CLI-specific scenarios
_CLI_MOCK_DATA = {
    # Mock response for section queries
    "en:action=query&explaintext=1&exsectionformat=wiki&format=json&prop=extracts&redirects=1&titles=CLI_Section_Test&": {
        "batchcomplete": "",
        "query": {
            "normalized": [{"from": "CLI_Section_Test", "to": "CLI Section Test"}],
            "pages": {
                "100": {
                    "pageid": 100,
                    "ns": 0,
                    "title": "CLI Section Test",
                    "extract": (
                        "Summary for CLI section test.\n\n\n"
                        + "== Section 1 ==\n"
                        + "Content for section 1.\n\n\n"
                        + "== Section 2 ==\n"
                        + "Content for section 2.\n\n\n"
                        + "=== Subsection 2.1 ===\n"
                        + "Content for subsection 2.1.\n\n\n"
                        + "== Section 3 ==\n"
                        + "Content for section 3."
                    ),
                }
            },
        },
    },
    # Mock response for backlinks
    "en:action=query&format=json&prop=backlinks&redirects=1&titles=CLI_Backlinks_Test&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "101": {
                    "pageid": 101,
                    "ns": 0,
                    "title": "CLI Backlinks Test",
                    "backlinks": [
                        {"ns": 0, "title": "Page linking to test 1"},
                        {"ns": 0, "title": "Page linking to test 2"},
                        {"ns": 14, "title": "Category linking to test"},
                    ],
                }
            },
        },
    },
    # Mock response for categories
    "en:action=query&format=json&prop=categories&redirects=1&titles=CLI_Categories_Test&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "102": {
                    "pageid": 102,
                    "ns": 0,
                    "title": "CLI Categories Test",
                    "categories": [
                        {"ns": 14, "title": "Category:Test Category 1"},
                        {"ns": 14, "title": "Category:Test Category 2"},
                    ],
                }
            },
        },
    },
    # Mock response for category members
    "en:action=query&format=json&prop=categorymembers&redirects=1&titles=Category:CLI_Test&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "103": {
                    "pageid": 103,
                    "ns": 14,
                    "title": "Category:CLI Test",
                    "categorymembers": [
                        {"ns": 0, "title": "CLI Test Page 1"},
                        {"ns": 0, "title": "CLI Test Page 2"},
                        {"ns": 14, "title": "Category:CLI Subcategory"},
                    ],
                }
            },
        },
    },
    # Mock response for non-existent page
    "en:action=query&explaintext=1&exsectionformat=wiki&format=json&prop=extracts&redirects=1&titles=CLI_Nonexistent_Test&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "-1": {
                    "ns": 0,
                    "title": "CLI Nonexistent Test",
                    "missing": "",
                }
            },
        },
    },
    # Add normalized version of Test_1 key for CLI tests
    "en:action=query&explaintext=1&exsectionformat=wiki&format=json&prop=extracts&redirects=1&titles=Test 1&": _MOCK_DATA.get(
        "en:action=query&explaintext=1&exsectionformat=wiki&format=json&prop=extracts&redirects=1&titles=Test_1&",
        {},
    ),
    # Add info queries for CLI tests
    "en:action=query&format=json&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle|varianttitles&prop=info&redirects=1&titles=Category:CLI_Test&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "103": {
                    "pageid": 103,
                    "ns": 14,
                    "title": "Category:CLI Test",
                    "contentmodel": "wikitext",
                    "pagelanguage": "en",
                    "pagelanguagehtmlcode": "en",
                    "pagelanguagedir": "ltr",
                    "protection": [],
                    "restrictiontypes": ["create"],
                    "notificationtimestamp": "",
                    "fullurl": "https://en.wikipedia.org/wiki/Category:CLI_Test",
                    "editurl": "https://en.wikipedia.org/w/index.php?title=Category:CLI_Test&action=edit",
                    "canonicalurl": "https://en.wikipedia.org/wiki/Category:CLI_Test",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "Category:CLI Test",
                }
            },
        },
    },
    # Add backlinks query for CLI tests
    "en:action=query&format=json&prop=backlinks&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "backlinks": [
                        {"ns": 0, "title": "Backlink Page 1"},
                        {"ns": 0, "title": "Backlink Page 2"},
                    ],
                }
            },
        },
    },
    # Add categories query for CLI tests
    "en:action=query&format=json&prop=categories&redirects=1&titles=Test_1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "categories": [
                        {"ns": 14, "title": "Category:Test Category 1"},
                        {"ns": 14, "title": "Category:Test Category 2"},
                    ],
                }
            },
        },
    },
    # Add categorymembers query for CLI tests
    "en:action=query&format=json&prop=categorymembers&redirects=1&titles=Category:CLI_Test&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "103": {
                    "pageid": 103,
                    "ns": 14,
                    "title": "Category:CLI Test",
                    "categorymembers": [
                        {"ns": 0, "title": "CLI Test Page 1"},
                        {"ns": 0, "title": "CLI Test Page 2"},
                        {"ns": 14, "title": "Category:CLI Subcategory"},
                    ],
                }
            },
        },
    },
    # Add normalized versions for common queries
    "en:action=query&format=json&prop=backlinks&redirects=1&titles=Test 1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "backlinks": [
                        {"ns": 0, "title": "Backlink Page 1"},
                        {"ns": 0, "title": "Backlink Page 2"},
                    ],
                }
            },
        },
    },
    "en:action=query&format=json&prop=categories&redirects=1&titles=Test 1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "categories": [
                        {"ns": 14, "title": "Category:Test Category 1"},
                        {"ns": 14, "title": "Category:Test Category 2"},
                    ],
                }
            },
        },
    },
    # Add categorymembers list query for CLI tests
    "en:action=query&cmlimit=500&cmtitle=Category:CLI Test&format=json&list=categorymembers&redirects=1&": {
        "batchcomplete": "",
        "query": {
            "categorymembers": [
                {"ns": 0, "title": "CLI Test Page 1", "pageid": 1001},
                {"ns": 0, "title": "CLI Test Page 2", "pageid": 1002},
                {"ns": 14, "title": "Category:CLI Subcategory", "pageid": 1003},
            ],
        },
    },
    # Add list-based queries for CLI tests
    "en:action=query&bllimit=500&bltitle=Test 1&format=json&list=backlinks&redirects=1&": {
        "batchcomplete": "",
        "query": {
            "backlinks": [
                {"ns": 0, "title": "Backlink Page 1", "pageid": 2001},
                {"ns": 0, "title": "Backlink Page 2", "pageid": 2002},
            ],
        },
    },
    "en:action=query&cllimit=500&format=json&prop=categories&redirects=1&titles=Test 1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "categories": [
                        {"ns": 14, "title": "Category:Test Category 1"},
                        {"ns": 14, "title": "Category:Test Category 2"},
                    ],
                }
            },
        },
    },
    "en:action=query&format=json&lllimit=500&llprop=url&prop=langlinks&redirects=1&titles=Test 1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "langlinks": [
                        {
                            "lang": "de",
                            "url": "https://de.wikipedia.org/wiki/Test",
                            "*": "Test Seite",
                        },
                        {
                            "lang": "fr",
                            "url": "https://fr.wikipedia.org/wiki/Test",
                            "*": "Page de test",
                        },
                    ],
                }
            },
        },
    },
    "en:action=query&format=json&pllimit=500&prop=links&redirects=1&titles=Test 1&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "links": [
                        {"ns": 0, "title": "Linked Page 1"},
                        {"ns": 0, "title": "Linked Page 2"},
                    ],
                }
            },
        },
    },
    # Add subcategory query for recursive category members
    "en:action=query&cmlimit=500&cmtitle=Category:CLI Subcategory&format=json&list=categorymembers&redirects=1&": {
        "batchcomplete": "",
        "query": {
            "categorymembers": [
                {"ns": 0, "title": "Subcategory Page", "pageid": 3001},
            ],
        },
    },
    # Add nonexistent category info query
    "en:action=query&format=json&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle|varianttitles&prop=info&redirects=1&titles=Category:Nonexistent&": {
        "batchcomplete": "",
        "query": {
            "pages": {
                "-1": {
                    "ns": 14,
                    "title": "Category:Nonexistent",
                    "missing": "",
                    "contentmodel": "wikitext",
                    "pagelanguage": "en",
                    "pagelanguagehtmlcode": "en",
                    "pagelanguagedir": "ltr",
                    "protection": [],
                    "restrictiontypes": ["create"],
                    "notificationtimestamp": "",
                    "fullurl": "https://en.wikipedia.org/wiki/Category:Nonexistent",
                    "editurl": "https://en.wikipedia.org/w/index.php?title=Category:Nonexistent&action=edit",
                    "canonicalurl": "https://en.wikipedia.org/wiki/Category:Nonexistent",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "Category:Nonexistent",
                }
            },
        },
    },
}

# Merge CLI mock data with main mock data
_MOCK_DATA.update(_CLI_MOCK_DATA)
