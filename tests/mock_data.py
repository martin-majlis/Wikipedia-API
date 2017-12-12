# -*- coding: utf-8 -*-


def wikipedia_api_request(params):
    query = ""
    for k in sorted(params.keys()):
        query += k + "=" + str(params[k]) + "&"

    return _MOCK_DATA[query]


_MOCK_DATA = {
    'action=query&explaintext=1&exsectionformat=wiki&prop=extracts&titles=Test_1&': {
        "batchcomplete": "",
        "warnings": {
            "extracts": {
                "*": "\"exlimit\" was too large for a whole article extracts request, lowered to 1."
            }
        },
        "query": {
            "normalized": [
                {
                    "from": "Test_1",
                    "to": "Test 1"
                }
            ],
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "extract": (
                        "Summary text\n\n\n\
                        == Section 1 ==\n\
                        Text for section 1\n\n\n\
                        === Section 1.1 ===\n\
                        Text for section 1.1\n\n\n\
                        === Section 1.2 ===\n\
                        Text for section 1.2\n\n\n \
                        == Section 2 ==\n \
                        Text for section 2\n\n\n \
                        == Section 3 ==\n \
                        Text for section 3\n\n\n \
                        == Section 4 ==\n\n\n \
                        === Section 4.1 ===\n \
                        Text for section 4.1\n\n\n \
                        === Section 4.2 ===\n \
                        Text for section 4.2\n\n\n \
                        ==== Section 4.2.1 ====\n \
                        Text for section 4.2.1\n\n\n \
                        ==== Section 4.2.2 ====\n \
                        Text for section 4.2.2\n\n\n \
                        == Section 5 ==\n \
                        Text for section 5\n\n\n \
                        === Section 5.1 ===\n \
                        Text for section 5.1\n\n\n \
                        "
                    )
                }
            }
        }
    },
    'action=query&prop=extracts&titles=Test_1&': {
        "batchcomplete": "",
        "warnings": {
            "extracts": {
                "*": "\"exlimit\" was too large for a whole article extracts request, lowered to 1."
            }
        },
        "query": {
            "normalized": [
                {
                    "from": "Test_1",
                    "to": "Test 1"
                }
            ],
            "pages": {
                "4": {
                    "pageid": 4,
                    "ns": 0,
                    "title": "Test 1",
                    "extract": (
                        "<p><b>Summary</b> text\n\n</p>\n\
                        <h2>Section 1</h2>\n\
                        <p>Text for section 1</p>\n\n\n\
                        <h3><span id=\"s1.1\">Section 1.1</span></h3>\n\
                        <p><b>Text for section 1.1</b>\n\n\n</p>\
                        <h3>Section 1.2</h3>\n\
                        <p><b>Text for section 1.2</b>\n\n\n</p>\
                        <h2><span id=\"s2\">Section 2</span></h2>\n\
                        <p><b>Text for section 2</b>\n\n\n</p>\
                        <h2><span id=\'s3\'>Section 3</span></h2>\n\
                        <p><b>Text for section 3</b>\n\n\n</p>\
                        <h2 id=\"s4\">Section 4</h2>\n\
                        <h3><span id=\"s4.1\">Section 4.1</span></h3>\n\
                        <p><b>Text for section 4.1</b>\n\n\n</p>\
                        <h3><span id=\"s4.2\">Section 4.2</span></h3>\n\
                        <p><b>Text for section 4.2</b>\n\n\n</p>\
                        <h4><span id=\"s4.2.1\">Section 4.2.1</span></h4>\n\
                        <p><b>Text for section 4.2.1</b>\n\n\n</p>\
                        <h4><span id=\"s4.2.2\">Section 4.2.2</span></h4>\n\
                        <p><b>Text for section 4.2.2</b>\n\n\n</p>\
                        <h2><span id=\"s5a\"></span><span id=\"s5b\">Section 5</span></h2>\n\
                        <p><b>Text for section 5</b>\n\n\n</p>\
                        <h3><span id=\"s5.1\">Section 5.1</span></h3>\n\
                        Text for section 5.1\n\n\n \
                        "
                    )
                }
            }
        }
    },
    'action=query&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle&prop=info&titles=Test_1&': {
        "batchcomplete": "",
        "query": {
            "normalized": [
                {
                    "from": "Test_1",
                    "to": "Test 1"
                }
            ],
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
                        {
                            "type": "create",
                            "level": "sysop",
                            "expiry": "infinity"
                        }
                    ],
                    "restrictiontypes": [
                        "create"
                    ],
                    "notificationtimestamp": "",
                    "fullurl": "https://en.wikipedia.org/wiki/Test_1",
                    "editurl": "https://en.wikipedia.org/w/index.php?title=Test_1&action=edit",
                    "canonicalurl": "https://en.wikipedia.org/wiki/Test_1",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "Test 1"
                }
            }
        }
    },
    'action=query&inprop=protection|talkid|watched|watchers|visitingwatchers|notificationtimestamp|subjectid|url|readable|preload|displaytitle&prop=info&titles=NonExisting&': {
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
                    "restrictiontypes": [
                        "create"
                    ],
                    "notificationtimestamp": "",
                    "fullurl": "https://en.wikipedia.org/wiki/NonExisting",
                    "editurl": "https://en.wikipedia.org/w/index.php?title=NonExisting&action=edit",
                    "canonicalurl": "https://en.wikipedia.org/wiki/NonExisting",
                    "readable": "",
                    "preload": None,
                    "displaytitle": "NonExisting"
                }
            }
        }
    },
    'action=query&lllimit=500&llprop=url&prop=langlinks&titles=Test_1&': {
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
                            "*": "Test 1 - 1"
                        },
                        {
                            "lang": "l2",
                            "url": "https://l2.wikipedia.org/wiki/Test_1_-_2",
                            "*": "Test 1 - 2"
                        },
                        {
                            "lang": "l3",
                            "url": "https://l3.wikipedia.org/wiki/Test_1_-_3",
                            "*": "Test 1 - 3"
                        },
                    ]
                }
            }
        }
    }
}
