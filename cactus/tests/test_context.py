#coding:utf-8
import os
from cactus.tests import SiteTestCase


class TestSiteContext(SiteTestCase):
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
        return {"context": {"a":"1", "b":True}}

    def test_site_context(self):
        """
        Test that the site context is provided.
        """
        self.assertEqual(
            sorted([page.source_path for page in self.site.context()['CACTUS']['pages']]),
            sorted(['error.html', 'index.html', 'test.html'])
        )

    def test_custom_context(self):
        """
        Test that custom context is provided
        """
        with open(os.path.join(self.site.build_path, "test.html")) as f:
            a, b = f.read().split("\n")

        self.assertEqual(a, "1")
        self.assertEqual(b, "True")

class TestCustomPageContext(SiteTestCase):
    """
    Test that custom context in the header of pages is feeded to a page

    Includes the built-in site context ('CACTUS'), and custom context.
    """
    def setUp(self):
        super(TestCustomPageContext, self).setUp()

        page = "a: 1\n\tb: Monkey\n{{ a }}\n{{ b }}"
        with open(os.path.join(self.site.page_path, "test.html"), "w") as f:
            f.write(page)

        self.site.build()

    def test_custom_context(self):
        """
        Test that custom context is provided
        """
        with open(os.path.join(self.site.build_path, "test.html")) as f:
            a, b = f.read().split("\n")

        self.assertEqual(a, "1")
        self.assertEqual(b, "Monkey")
