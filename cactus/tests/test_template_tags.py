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

class TestStaticLookup(SiteTestCase):
    """
    {% static %} should auto append static
    """
    # def setUp(self):
    #     super(TestStaticLookup, self).setUp()

    def test_prepend_exists(self):

        with open(os.path.join(self.site.static_path, "exists.js"), "w") as f:
            f.write("hello")

        with open(os.path.join(self.site.page_path, "test1.html"), "w") as f:
            f.write("{% static '/exists.js' %}")

        with open(os.path.join(self.site.page_path, "test2.html"), "w") as f:
            f.write("{% static 'exists.js' %}")

        self.site.build()

        with(open(os.path.join(self.site.build_path, "test1.html"))) as f:
            self.assertEqual(f.read(), "/static/exists.js")

        with(open(os.path.join(self.site.build_path, "test2.html"))) as f:
            self.assertEqual(f.read(), "/static/exists.js")

    def test_prepend_nonexists(self):

        with open(os.path.join(self.site.page_path, "test.html"), "w") as f:
            f.write("{% static '/notexists.js' %}")

        self.site.build()

        with(open(os.path.join(self.site.build_path, "test.html"))) as f:
            self.assertEqual(f.read(), "/notexists.js")

class TestStaticRelative(SiteTestCase):

    def doit(self, static_subdir, page_subdir, page_contents, output):

        full_static_subdir = os.path.join(self.site.static_path, static_subdir)
        full_page_subdir = os.path.join(self.site.page_path, page_subdir)

        try: os.makedirs(full_static_subdir)
        except: pass

        try: os.makedirs(full_page_subdir)
        except: pass

        # Write the static file
        with open(os.path.join(full_static_subdir, "test.js"), "w") as f:
            f.write("hello")

        # Write the page with contents
        with open(os.path.join(full_page_subdir, "test.html"), "w") as f:
            f.write(page_contents)

        self.site.build()

        with(open(os.path.join(self.site.build_path, page_subdir, "test.html"))) as f:
            self.assertEqual(f.read(), output)

    def test_simple(self):
        self.doit("", "", "{% static 'static/test.js' %}", "static/test.js")

    # I'm not sure if we should do this at all

    # def test_relative(self):
    #     self.doit("", "docs", "{% static 'static/test.js' %}", "../static/test.js")




class TestMarkdown(SiteTestCase):

    def test_tags(self):

        for level in [1, 2, 3, 4, 5]:

            levelStr = "#" * level

            with open(os.path.join(self.site.page_path, "test.html"), "w") as f:
                f.write("{% filter markdown %}" + levelStr + " Hello{% endfilter %}")

            self.site.build()

            with open(os.path.join(self.site.build_path, "test.html")) as f:
                self.assertEqual(f.read(), "<h%s>Hello</h%s>\n" % (level, level))

class TestConfig(SiteTestCase):

    def setUp(self):
        super(TestConfig, self).setUp()

        self.site.config.set("test-value", "yep")

    def test_config_value(self):

        with open(os.path.join(self.site.page_path, "test.html"), "w") as f:
            f.write("{% config 'test-value' %}")

        self.site.build()

        with open(os.path.join(self.site.build_path, "test.html")) as f:
            self.assertEqual(f.read(), "yep")

    def test_no_config_value(self):

        with open(os.path.join(self.site.page_path, "test.html"), "w") as f:
            f.write("{% config 'unknown' %}")

        self.site.build()

        with open(os.path.join(self.site.build_path, "test.html")) as f:
            self.assertEqual(f.read(), "")
