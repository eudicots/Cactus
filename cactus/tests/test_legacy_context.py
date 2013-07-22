#coding:utf-8
import os

from cactus.tests import SiteTestCase


class TestLegacyContext(SiteTestCase):
    def setUp(self):
        super(TestLegacyContext, self).setUp()
        os.mkdir(os.path.join(self.site.page_path, "test"))

        with open(os.path.join(self.site.page_path, "static.html"), "w") as f:
            f.write("{{ STATIC_URL }}")

        with open(os.path.join(self.site.page_path, "test", "static.html"), "w") as f:
            f.write("{{ STATIC_URL }}")

        with open(os.path.join(self.site.page_path, "root.html"), "w") as f:
            f.write("{{ ROOT_URL }}")

        with open(os.path.join(self.site.page_path, "test", "root.html"), "w") as f:
            f.write("{{ ROOT_URL }}")

        with open(os.path.join(self.site.page_path, "page.html"), "w") as f:
            f.write("{{ PAGE_URL }}")

    def test_context(self):
        self.site.build()

        with open(os.path.join(self.site.build_path, "static.html")) as f:
            self.assertEqual(f.read(), "./static")

        with open(os.path.join(self.site.build_path, "test", "static.html")) as f:
            self.assertEqual(f.read(), "../static")

        with open(os.path.join(self.site.build_path, "root.html")) as f:
            self.assertEqual(f.read(), ".")

        with open(os.path.join(self.site.build_path, "test", "root.html")) as f:
            self.assertEqual(f.read(), "..")

        with open(os.path.join(self.site.build_path, "page.html")) as f:
            self.assertEqual(f.read(), "page.html")

    def test_pretty_urls(self):
        self.site.prettify_urls = True

        self.site.build()

        with open(os.path.join(self.site.build_path, "test", "static", "index.html")) as f:
            self.assertEqual(f.read(), "../../static")

        with open(os.path.join(self.site.build_path, "root", "index.html")) as f:
            self.assertEqual(f.read(), "..")

        with open(os.path.join(self.site.build_path, "test", "root", "index.html")) as f:
            self.assertEqual(f.read(), "../..")

        with open(os.path.join(self.site.build_path, "page", "index.html")) as f:
            self.assertEqual(f.read(), "page/")
