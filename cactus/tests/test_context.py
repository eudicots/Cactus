#coding:utf-8
import os
import unittest
from cactus.tests import SiteTest

from cactus.variables import parse_site_variable


class TestContext(unittest.TestCase):
    """
    Test that context variable parsing works.
    """
    def test_variables(self):
        self.assertEqual(('a', 'b'), parse_site_variable('a=b'))
        self.assertEqual(('a', True), parse_site_variable('a'))


class TestSiteContext(SiteTest):
    """
    Test that the proper context is provided to the pages

    Includes the built-in site context ('CACTUS'), and custom context.
    """
    def setUp(self):
        super(TestSiteContext, self).setUp()

        page = "{{ a }}\n{{ b }}"
        with open(os.path.join(self.site.page_path, "test.html"), "w") as f:
            f.write(page)

        self.site.build()

    def get_config_for_test(self):
        return {"variables": {"a":"1", "b":True}}

    def test_site_context(self):
        """
        Test that the site context is provided.
        """
        self.assertEqual(
            [page.source_path for page in self.site.context()['CACTUS']['pages']],
            ['error.html', 'index.html', 'test.html']
        )

    def test_custom_context(self):
        """
        Test that custom variables are provided
        """
        with open(os.path.join(self.site.build_path, "test.html")) as f:
            a, b = f.read().split("\n")

        self.assertEqual(a, "1")
        self.assertEqual(b, "True")