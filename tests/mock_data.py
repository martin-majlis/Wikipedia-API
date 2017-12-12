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
    }
}
