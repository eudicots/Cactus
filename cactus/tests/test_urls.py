#coding:utf-8
import os

from cactus.tests import SiteTestCase


class TestPrettyURLS(SiteTestCase):
    def get_config_for_test(self):
        return {"prettify": True}

    def setUp(self):
        super(TestPrettyURLS, self).setUp()

        open(os.path.join(self.path, 'pages', 'test.html'), 'w')
        subfolder = os.path.join(self.path, 'pages', 'folder')
        os.makedirs(subfolder)
        open(os.path.join(subfolder, 'index.html'), 'w')
        open(os.path.join(subfolder, 'page.html'), 'w')


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
        self.assertRaises(IOError, open, os.path.join(self.path, '.build', 'test.html'), 'rU')

    def test_ignore_non_html(self):
        """
        Check that we don't rewrite paths for .txt files.
        """
        self.assertFileExists(os.path.join(self.site.build_path, 'sitemap.xml'))
        self.assertFileExists(os.path.join(self.site.build_path, 'robots.txt'))
