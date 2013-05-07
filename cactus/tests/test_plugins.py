#coding:utf-8
import shutil
import os

from cactus import Site
from cactus.tests import SiteTest


class TestPluginLoader(SiteTest):
    def setUp(self):
        super(TestPluginLoader, self).setUp()
        self.site = Site(self.path, self.config_path)

        shutil.rmtree(self.site.plugin_path)
        os.makedirs(self.site.plugin_path)

    def _load_test_plugin(self, to_filename):
        src_path = os.path.join('cactus', 'tests', 'data', 'plugin.py')
        dst_path = os.path.join(self.site.plugin_path, to_filename)
        shutil.copy(src_path, dst_path)

    def test_ignore_disabled(self):
        self._load_test_plugin('test.disabled.py')
        self.site.loadPlugins()
        self.assertEqual([], self.site._plugins)

    def test_load_plugin(self):
        self._load_test_plugin('test.py')
        self.site.loadPlugins()
        self.assertEqual(1, len(self.site._plugins))
        self.assertEqual('plugin_test', self.site._plugins[0].__name__)
