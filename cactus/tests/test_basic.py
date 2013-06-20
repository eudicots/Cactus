import os
import codecs

from cactus.site import Site
from cactus.tests import SiteTest
from cactus.utils.filesystem import fileList


def readFile(path):
    f = codecs.open(path, 'r', 'utf8')
    d = f.read()
    f.close()
    return d


def writeFile(path, data):
    f = codecs.open(path, 'w', 'utf8')
    f.write(data)
    f.close()


def mockFile(name):
    return readFile(os.path.join('cactus', 'tests', 'data', name))


class TestSite(SiteTest):
    def setUp(self):
        super(TestSite, self).setUp()

        self.site = Site(self.path, self.config_path)

    def testBuild(self):
        """
        Test that we build the proper files.
        """
        self.site.build()

        # Make sure we build to .build and not build
        self.assertEqual(os.path.exists(os.path.join(self.path, 'build')), False)

        self.assertEqual(fileList(os.path.join(self.path, '.build'), relative=True), [
            'error.html',
            'index.html',
            'robots.txt',
            'sitemap.xml',
            self.site.get_url_for_static('/static/css/style.css')[1:],  # Strip the initial /
            self.site.get_url_for_static('/static/images/favicon.ico')[1:],  # Strip the initial /
            self.site.get_url_for_static('/static/js/main.js')[1:],  # Strip the initial /
        ])

    def testRenderPage(self):
        """
        Test that pages get rendered.
        """

        writeFile(
            os.path.join(self.path, 'pages', 'test.html'),
            mockFile('test-in.html')
        )

        self.site.build()

        self.assertEqual(
            readFile(os.path.join(self.path, '.build', 'test.html')),
            mockFile('test-out.html')
        )

    def testPageContext(self):
        """
        Test that page context is parsed and uses in the pages.
        """

        writeFile(
            os.path.join(self.path, 'pages', 'koenpage.html'),
            mockFile('koenpage-in.html')
        )

        self.site.build()

        self.assertEqual(
            readFile(os.path.join(self.path, '.build', 'koenpage.html')),
            mockFile('koenpage-out.html')
        )

    def test_html_only_context(self):
        """
        Test that we only parse context on HTML pages.
        """
        robots_txt = 'Disallow:/page1\nDisallow:/page2'

        with open(os.path.join(self.site.path, 'pages', 'robots.txt'), 'w') as f:
            f.write(robots_txt)

        self.site.build()

        with open(os.path.join(self.site.build_path, 'robots.txt')) as f:
            self.assertEquals(robots_txt, f.read())

    def testStaticLoader(self):
        """
        Test that the static URL builde and template tag work.
        """
        static = '/static/css/style.css'
        page = "{%% static '%s' %%}" % static

        writeFile(
            os.path.join(self.path, 'pages', 'staticpage.html'),
            page
        )

        self.site.build()

        self.assertEqual(
            readFile(os.path.join(self.path, '.build', 'staticpage.html')),
            self.site.get_url_for_static(static)
        )

    def test_current_page(self):
        """
        Test that the if_current_page tag works.
        """
        page = 'page1.html'
        content = "{%% if_current_page '/%s' %%}" % page

        other = 'page2.html'

        with open(os.path.join(self.path, 'pages', page), 'w') as f:
            f.write(content)

        with open(os.path.join(self.path, 'pages', other), 'w') as f:
            f.write(content)

        self.site.build()

        with open(os.path.join(self.path, '.build', page)) as f:
            self.assertEqual('True', f.read())

        with open(os.path.join(self.path, '.build', other)) as f:
            self.assertEqual('False', f.read())
