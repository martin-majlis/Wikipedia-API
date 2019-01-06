import unittest

import wikipediaapi


class TestRequest(unittest.TestCase):
    query = 'Arthur Schopenhauer'

    def test_request_without_kwargs(self):
        wiki = wikipediaapi.Wikipedia()

        try:
            page = wiki.page(self.query)
            page.summary
        except Exception as e:
            self.fail(
                'TestRequest::test_request_without_kwargs '
                'failed due to the exception: ' + str(e)
            )

    def test_request_with_kwargs(self):
        wiki = wikipediaapi.Wikipedia(timeout=30.0)

        try:
            page = wiki.page(self.query)
            page.summary
        except Exception as e:
            self.fail(
                'TestRequest::test_request_with_kwargs '
                'failed due to the exception: ' + str(e)
            )
