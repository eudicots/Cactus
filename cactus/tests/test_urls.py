#coding:utf-8
import os
from cactus import Site
from cactus.tests import SiteTest


class TestPrettyURLS(SiteTest):
    def setUp(self):
        super(TestPrettyURLS, self).setUp()

        self.conf.set('prettify', True)
        self.conf.write()

        self.site = Site(self.path, self.config_path)

        with open(os.path.join(self.path, 'pages', 'test.html'), 'w') as f:
            pass

        subfolder = os.path.join(self.path, 'pages', 'folder')
        os.makedirs(subfolder)
        with open(os.path.join(subfolder, 'index.html'), 'w') as f:
            pass
        with open(os.path.join(subfolder, 'page.html'), 'w') as f:
            pass


        self.site.build()

    def test_get_path(self):
        """
        Test that URL rewriting makes pretty links.
        """
        self.assertEqual(self.site.get_url_for_page('/index.html'), '/')
        self.assertEqual(self.site.get_url_for_page('/test.html'), '/test/')
        self.assertEqual(self.site.get_url_for_page('/folder/index.html'), '/folder/')
        self.assertEqual(self.site.get_url_for_page('/folder/page.html'), '/folder/page/')

    def test_build_page(self):
        """
        Check that we rewrite paths for .html files.
        """
        self.assertFileExists(os.path.join(self.site.build_path, 'index.html'))
        self.assertFileExists(os.path.join(self.site.build_path, 'test', 'index.html'))
        self.assertFileExists(os.path.join(self.site.build_path, 'folder', 'index.html'))
        self.assertFileExists(os.path.join(self.site.build_path, 'folder', 'page', 'index.html'))
        self.assertRaises(IOError, open, os.path.join(self.path, '.build', 'test.html'))

    def test_ignore_non_html(self):
        """
        Check that we don't rewrite paths for .txt files.
        """
        self.assertFileExists(os.path.join(self.site.build_path, 'sitemap.xml'))
        self.assertFileExists(os.path.join(self.site.build_path, 'robots.txt'))