# flake8: noqa

user_agent = "UnitTests (bot@example.com)"


def wikipedia_api_request(wiki):
    def api_request(page, params):
        used_params = wiki._construct_params(page, params)
        query = ""
        for k in sorted(used_params.keys()):
            query += k + "=" + str(used_params[k]) + "&"

        return _MOCK_DATA[page.language + ":" + query]

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
                    "protection": [
                        {"type": "create", "level": "sysop", "expiry": "infinity"}
                    ],
                    "restrictiontypes": ["create"],
                    "notificationtimestamp": "",
                    "fullurl": "https://en.wikipedia.org/wiki/Test_1",
                    "editurl": "https://en.wikipedia.org/w/index.php?title=Test_1&action=edit",
                    "canonicalurl": "https://en.wikipedia.org/wiki/Test_1",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "Test 1",
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
                    "protection": [
                        {"type": "create", "level": "sysop", "expiry": "infinity"}
                    ],
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
                    "protection": [
                        {"type": "create", "level": "sysop", "expiry": "infinity"}
                    ],
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
                    "protection": [
                        {"type": "create", "level": "sysop", "expiry": "infinity"}
                    ],
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
                    "protection": [
                        {"type": "create", "level": "sysop", "expiry": "infinity"}
                    ],
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
}
