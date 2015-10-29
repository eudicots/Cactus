# coding:utf-8
import os

from cactus.tests import SiteTestCase


class TestPrefixedURLS(SiteTestCase):
    def get_config_for_test(self):
        return {
            "prettify": True,
            "page-prefix": "/abc",
            "static-prefix": "/def",
        }

    def setUp(self):
        super(TestPrefixedURLS, self).setUp()

        open(os.path.join(self.path, 'pages', 'test.html'), 'w')
        subfolder = os.path.join(self.path, 'pages', 'folder')
        os.makedirs(subfolder)
        open(os.path.join(subfolder, 'index.html'), 'w')
        open(os.path.join(subfolder, 'page.html'), 'w')

        open(os.path.join(self.path, 'static', 'blabla.png'), 'w')
        subfolder = os.path.join(self.path, 'static', 'folder')
        os.makedirs(subfolder)
        open(os.path.join(subfolder, 'favicon.ico'), 'w')


        self.site.build()

    def test_get_path_for_pages(self):
        """
        Test that URL rewriting includes page prefix for pages.
        """
        self.assertEqual(self.site.get_url_for_page('/index.html'), '/abc/')
        self.assertEqual(self.site.get_url_for_page('/test.html'), '/abc/test/')
        self.assertEqual(self.site.get_url_for_page('/folder/index.html'), '/abc/folder/')
        self.assertEqual(self.site.get_url_for_page('/folder/page.html'), '/abc/folder/page/')

    def test_get_path_for_static(self):
        """
        Test that URL rewriting includes static prefix for static ressources.
        """
        self.assertEqual(self.site.get_url_for_static('/static/blabla.png'), '/def/static/blabla.png')
        self.assertEqual(self.site.get_url_for_static('/static/folder/index.html'), '/def/static/folder/favicon.css')
