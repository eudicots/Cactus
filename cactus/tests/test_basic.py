#coding:utf-8
import os
import shutil

from cactus.tests import SiteTestCase
from cactus.utils.filesystem import fileList
from cactus.utils.url import path_to_url


class TestSite(SiteTestCase):
    def testBuild(self):
        """
        Test that we build the proper files.
        """
        self.site.build()

        # Make sure we build to .build and not build
        self.assertEqual(os.path.exists(os.path.join(self.path, 'build')), False)

        self.assertEqual(
            sorted([path_to_url(path) for path in fileList(os.path.join(self.path, '.build'), relative=True)]),
            sorted([
                'error.html',
                'index.html',
                'robots.txt',
                'sitemap.xml',
                self.site.get_url_for_static('/static/css/style.css')[1:],  # Strip the initial /
                self.site.get_url_for_static('/static/images/favicon.ico')[1:],  # Strip the initial /
                self.site.get_url_for_static('/static/js/main.js')[1:],  # Strip the initial /
        ]))

    def testRenderPage(self):
        """
        Test that pages get rendered.
        """

        shutil.copy(
            os.path.join('cactus', 'tests', 'data', "test-in.html"),
            os.path.join(self.path, 'pages', 'test.html')
        )


        self.site.build()

        with open(os.path.join('cactus', 'tests', 'data', 'test-out.html'), "rU") as expected:
            with open(os.path.join(self.path, '.build', 'test.html'), "rU") as obtained:
                self.assertEqual(expected.read(), obtained.read())

    def testPageContext(self):
        """
        Test that page context is parsed and uses in the pages.
        """

        shutil.copy(
            os.path.join('cactus', 'tests', 'data', "koenpage-in.html"),
            os.path.join(self.path, 'pages', 'koenpage.html')
        )

        self.site.build()

        with open(os.path.join('cactus', 'tests', 'data', 'koenpage-out.html'), "rU") as expected:
            with open(os.path.join(self.path, '.build', 'koenpage.html'), "rU") as obtained:
                self.assertEqual(expected.read(), obtained.read())

    def test_html_only_context(self):
        """
        Test that we only parse context on HTML pages.
        """
        robots_txt = 'Disallow:/page1\nDisallow:/page2'

        with open(os.path.join(self.site.path, 'pages', 'robots.txt'), 'w') as f:
            f.write(robots_txt)

        self.site.build()

        with open(os.path.join(self.site.build_path, 'robots.txt'), 'rU') as f:
            self.assertEquals(robots_txt, f.read())

    def testStaticLoader(self):
        """
        Test that the static URL builde and template tag work.
        """
        static = '/static/css/style.css'
        page = "{%% static '%s' %%}" % static


        with open(os.path.join(self.path, 'pages', 'staticpage.html'), "w") as dst:
            dst.write(page)

        self.site.build()

        with open(os.path.join(self.path, '.build', 'staticpage.html'), "rU") as obtained:
            self.assertEqual(self.site.get_url_for_static(static), obtained.read())

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

        with open(os.path.join(self.path, '.build', page), 'rU') as f:
            self.assertEqual('True', f.read())

        with open(os.path.join(self.path, '.build', other), 'rU') as f:
            self.assertEqual('False', f.read())
