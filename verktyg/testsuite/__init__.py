"""
    verktyg.testsuite
    ~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 by Ben Mather.
    :license: BSD, see LICENSE for more details.
"""
import unittest

from verktyg.testsuite import (
    test_accept, test_application, test_dispatch,
    test_routing, test_views, test_wrappers,
)


loader = unittest.TestLoader()
suite = unittest.TestSuite((
    loader.loadTestsFromModule(test_accept),
    loader.loadTestsFromModule(test_application),
    loader.loadTestsFromModule(test_dispatch),
    loader.loadTestsFromModule(test_routing),
    loader.loadTestsFromModule(test_views),
    loader.loadTestsFromModule(test_wrappers),
))
