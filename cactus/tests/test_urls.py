#coding:utf-8
import os
from cactus import Site
from cactus.config import Config
from cactus.tests import BaseTest


class TestPrettyURLS(BaseTest):
    def setUp(self):
        super(TestPrettyURLS, self).setUp()

        config_path = os.path.join(self.path, 'config.json')
        conf = Config(config_path)
        conf.set('site-url', 'http://example.com/')
        conf.set('prettify', True)
        conf.write()

        self.site = Site(self.path, config_path)
        self.build_path = self.site.paths['build']

        with open(os.path.join(self.path, 'pages', 'test.html'), 'w') as f:
            f.write('Placeholder')

        self.site.build()

    def test_get_path(self):
        self.assertEqual(self.site.get_path_for_page('/test.html'), '/test/')
        self.assertEqual(self.site.get_path_for_page('/index.html'), '/index/')

    def test_build_page(self):
        """
        Check that we rewrite paths for .html files
        """
        self.assertFileExists(os.path.join(self.build_path, 'index.html'))
        self.assertFileExists(os.path.join(self.build_path, 'test', 'index.html'))
        self.assertRaises(IOError, open, os.path.join(self.path, '.build', 'test.html'))

    def test_ignore_non_html(self):
        """
        Check that we don't rewrite paths for .txt files
        """
        self.assertFileExists(os.path.join(self.build_path, 'sitemap.xml'))
        self.assertFileExists(os.path.join(self.build_path, 'robots.txt'))