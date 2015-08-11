"""
    verktyg.testsuite
    ~~~~~~~~~~~~~~~~~

    :copyright:
        (c) 2015 Ben Mather, based on Werkzeug, see AUTHORS for more details.
    :license:
        BSD, see LICENSE for more details.

"""
import unittest

from verktyg.testsuite import (
    test_headers, test_accept, test_application, test_dispatch,
    test_exceptions, test_routing, test_views, test_requests, test_responses,
    test_wsgi,
)


loader = unittest.TestLoader()
suite = unittest.TestSuite((
    loader.loadTestsFromModule(test_headers),
    loader.loadTestsFromModule(test_accept),
    loader.loadTestsFromModule(test_application),
    loader.loadTestsFromModule(test_dispatch),
    loader.loadTestsFromModule(test_exceptions),
    loader.loadTestsFromModule(test_routing),
    loader.loadTestsFromModule(test_views),
    loader.loadTestsFromModule(test_requests),
    loader.loadTestsFromModule(test_responses),
    loader.loadTestsFromModule(test_wsgi),
))
