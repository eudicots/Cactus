#coding:utf-8
import os
import shutil

from cactus.plugin.loader import CustomPluginsLoader
from cactus.plugin.manager import PluginManager
from cactus.tests import SiteTestCase


class TestPluginLoader(SiteTestCase):
    def setUp(self):
        super(TestPluginLoader, self).setUp()
        self.site.plugin_manager = PluginManager(self.site, [CustomPluginsLoader(self.site.path)])
        shutil.rmtree(self.site.plugin_path)
        os.makedirs(self.site.plugin_path)

    def _load_test_plugin(self, plugin, to_filename):
        src_path = os.path.join('cactus', 'tests', 'data', 'plugins', plugin)
        dst_path = os.path.join(self.site.plugin_path, to_filename)
        shutil.copy(src_path, dst_path)
        self.site.plugin_manager.reload()

    def test_ignore_disabled(self):
        self._load_test_plugin('test.py', 'test.disabled.py')
        self.assertEqual([], [p for p in self.site.plugin_manager.plugins if not p.builtin])

    def test_load_plugin(self):
        self._load_test_plugin('test.py', 'test.py')

        plugins = self.site.plugin_manager.plugins
        self.assertEqual(1, len(plugins ))
        self.assertEqual('plugin_test', plugins[0].plugin_name)
        self.assertEqual(2, plugins[0].ORDER)

    def test_defaults(self):
        """
        Check that defaults get initialized
        """
        self._load_test_plugin('empty.py', 'empty.py')
        plugins = self.site.plugin_manager.plugins

        plugin = plugins[0]
        self.assert_(hasattr(plugin, 'preBuild'))
        self.assert_(hasattr(plugin, 'postBuild'))
        self.assertEqual(-1, plugin.ORDER)

    def test_call(self):
        """
        Check that plugins get called
        """
        self._load_test_plugin('test.py', 'call.py')
        plugins = self.site.plugin_manager.plugins

        plugin = plugins[0]

        self.assertEqual('plugin_call', plugin.plugin_name)  # Just to check we're looking at the right one.

        self.site.build()

        # preBuild
        self.assertEqual(1, len(plugin.preBuild.calls))
        self.assertEqual((self.site,), plugin.preBuild.calls[0]['args'])

        # preBuildPage
        self.assertEqual(len(self.site.pages()), len(plugin.preBuildPage.calls))
        for call in plugin.preBuildPage.calls:
            self.assertIn(len(call['args']), (3, 4))

        # postBuildPage
        self.assertEqual(len(self.site.pages()), len(plugin.postBuildPage.calls))

        #postBuild
        self.assertEqual(1, len(plugin.postBuild.calls))
        self.assertEqual((self.site,), plugin.postBuild.calls[0]['args'])
