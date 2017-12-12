# -*- coding: utf-8 -*-


def wikipedia_api_request(params):
    query = ""
    for k in sorted(params.keys()):
        query += k + "=" + str(params[k]) + "&"

    return _MOCK_DATA[query]


_MOCK_DATA = {
    'action=query&explaintext=True&prop=extracts&titles=Test_1&': {
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
                        Text for section 2\n\n\n \
                        === Section 5.1 ===\n \
                        Text for section 1.1\n\n\n \
                        "
                    )
                }
            }
        }
    }
}
