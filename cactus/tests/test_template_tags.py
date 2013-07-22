#coding:utf-8
import os

from cactus.tests import SiteTestCase


class TestPageTags(SiteTestCase):
    """
    {% current_page %} should return the URL the user is currently seeing.
    {% url 'page.html' %} should return the link to a page
    {% if_current_page 'page.html' 1 0 %} should return 1 if we're on this page, 0 otherwise
    """
    def setUp(self):
        super(TestPageTags, self).setUp()

        with open(os.path.join(self.site.page_path, "test.html"), "w") as f:
            f.write("{% current_page %}")

        with open(os.path.join(self.site.page_path, "link.html"), "w") as f:
            f.write("{% url '/test.html' %}")

        with open(os.path.join(self.site.page_path, "if-yes.html"), "w") as f:
            f.write("{% if_current_page '/if-yes.html' 1 0 %}")

        with open(os.path.join(self.site.page_path, "if-no.html"), "w") as f:
            f.write("{% if_current_page '/if-yes.html' 1 0 %}")

    def test_regular_urls(self):
        self.site.build()

        with open(os.path.join(self.site.build_path, "test.html")) as f:
            self.assertEqual(f.read(), "/test.html")

        with open(os.path.join(self.site.build_path, "link.html")) as f:
            self.assertEqual(f.read(), "/test.html")

        with open(os.path.join(self.site.build_path, "if-yes.html")) as f:
            self.assertEqual(f.read(), "1")

        with open(os.path.join(self.site.build_path, "if-no.html")) as f:
            self.assertEqual(f.read(), "0")

    def test_pretty_urls(self):
        self.site.prettify_urls = True  #TOOD: should be read at runtime
        self.site.build()

        with open(os.path.join(self.site.build_path, "test", "index.html")) as f:
            self.assertEqual(f.read(), "/test/")

        with open(os.path.join(self.site.build_path, "link", "index.html")) as f:
            self.assertEqual(f.read(), "/test/")

        with open(os.path.join(self.site.build_path, "if-yes", "index.html")) as f:
            self.assertEqual(f.read(), "1")

        with open(os.path.join(self.site.build_path, "if-no", "index.html")) as f:
            self.assertEqual(f.read(), "0")


class TestStatic(SiteTestCase):
    """
    {% static %} should convert from a link_url to a final_url
    """
    def setUp(self):
        super(TestStatic, self).setUp()

        with open(os.path.join(self.site.page_path, "test.html"), "w") as f:
            f.write("{% static '/static/js/main.js' %}")

    def test_no_fingerprints(self):
        self.site.build()

        with(open(os.path.join(self.site.build_path, "test.html"))) as f:
            self.assertEqual(f.read(), "/static/js/main.js")

    def test_fingerprint(self):
        self.site.build()

        expected = None

        for static in self.site.static():
            if static.src_filename == "main.js":
                expected = static.final_url

        self.assertIsNotNone(expected)  # Was the JS built?

        with open(os.path.join(self.site.build_path, "test.html")) as f:
            self.assertEqual(f.read(), expected)
