#coding:utf-8
import shutil
import os

from cactus import Site
from cactus.tests import SiteTest


class TestPluginLoader(SiteTest):
    def setUp(self):
        super(TestPluginLoader, self).setUp()
        self.site = Site(self.path, self.config_path)
        self.site.setup()  # Load the plugin manager

        shutil.rmtree(self.site.plugin_path)
        os.makedirs(self.site.plugin_path)


    def _load_test_plugin(self, plugin, to_filename):
        src_path = os.path.join('cactus', 'tests', 'data', 'plugins', plugin)
        dst_path = os.path.join(self.site.plugin_path, to_filename)
        shutil.copy(src_path, dst_path)
        self.site.plugin_manager.reload()

    def test_ignore_disabled(self):
        self._load_test_plugin('test.py', 'test.disabled.py')
        self.assertEqual([], self.site.plugin_manager.plugins)

    def test_load_plugin(self):
        self._load_test_plugin('test.py', 'test.py')
        self.assertEqual(1, len(self.site.plugin_manager.plugins))
        self.assertEqual('plugin_test', self.site.plugin_manager.plugins[0].__name__)
        self.assertEqual(2, self.site.plugin_manager.plugins[0].ORDER)

    def test_defaults(self):
        """
        Check that defaults get initialized
        """
        self._load_test_plugin('empty.py', 'test.py')
        plugin = self.site.plugin_manager.plugins[0]
        self.assertEqual(-1, plugin.ORDER)
        self.assert_(hasattr(plugin, 'preBuild'))
        self.assert_(hasattr(plugin, 'postBuild'))