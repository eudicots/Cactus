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

    def _load_test_plugin(self, plugin, to_filename):
        src_path = os.path.join('cactus', 'tests', 'data', 'plugins', plugin)
        dst_path = os.path.join(self.site.plugin_path, to_filename)
        shutil.copy(src_path, dst_path)

    def test_ignore_disabled(self):
        self._load_test_plugin('test.py', 'test.disabled.py')
        self.assertEqual([], self.site.plugins)

    def test_load_plugin(self):
        self._load_test_plugin('test.py', 'test.py')
        self.assertEqual(1, len(self.site.plugins))
        self.assertEqual('plugin_test', self.site.plugins[0].__name__)
        self.assertEqual(2, self.site.plugins[0].ORDER)

    def test_defaults(self):
        """
        Check that defaults get initialized
        """
        self._load_test_plugin('empty.py', 'test.py')
        plugin = self.site.plugins[0]
        self.assertEqual(-1, plugin.ORDER)
        self.assert_(hasattr(plugin, 'preBuild'))
        self.assert_(hasattr(plugin, 'postBuild'))