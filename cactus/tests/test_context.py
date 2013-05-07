#coding:utf-8
import unittest

from cactus.variables import parse_site_variable


class TestContext(unittest.TestCase):
    """
    Test that context variable parsing works.
    """
    def test_variables(self):
        self.assertEqual(('a', 'b'), parse_site_variable('a=b'))
        self.assertEqual(('a', True), parse_site_variable('a'))
