#coding:utf-8
import os
import shutil
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from testfixtures import LogCapture

from cactus.plugin.loader import CustomPluginsLoader
from cactus.plugin.manager import PluginManager
from cactus.tests import SiteTestCase
from cactus.plugin.builtin.pagecontext import PageContextPlugin

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


class TestPagecontextPlugin(unittest.TestCase):

    def test_jekyll_style(self):
        testdata = [
            (['---',  # fenced
              'Author : Me',
              'Content: Awesome',
              '---',
              'Here comes the content'],
             {'Author': 'Me', 'Content': 'Awesome'},
             ['Here comes the content']),

            (['Author : Me',  # no start of metadata
              '---',
              'Here comes the content'],
             {},
             ['Author : Me',
              '---',
              'Here comes the content']),

            (['',  # file starts with a blank line
              '---',
              'Todays motto: whatever'],
             {},  # no context data
             ['', '---', 'Todays motto: whatever']),  # everything preserved

            (['This file has',
              'no metadata whatsoever'],
             {},
             ['This file has', 'no metadata whatsoever']),

        ]
        plugin = PageContextPlugin()

        for i, (lines, context, data) in enumerate(testdata):
            self.assertEqual((context, data), 
                             plugin.jekyll_style(lines),
                             'Test Data No. %d failed' % i)

        lines = ['---',
                 'Author : Me',  # no end of metadata
                 'Here comes the content']
        with LogCapture() as l:
            context, data = plugin.jekyll_style(lines)
        self.assertEqual(len(l.records), 1)
        self.assertEqual(l.records[0].levelname, 'WARNING')
        self.assertEqual(l.records[0].msg, 'Page context data seem to end in line %d')

    def test_simple_style(self):
        testdata = [
            (['Author : Me',
              'Content: Awesome',
              '',
              'Here comes the content'],
             {'Author': 'Me', 'Content': 'Awesome'},
             ['', 'Here comes the content']),

            (['',  # file starts with a blank line
              'Todays motto: whatever'],
             {},  # no context data
             ['', 'Todays motto: whatever']),  # blank line preserved

            (['This file has',
              'no metadata whatsoever'],
             {},
             ['This file has', 'no metadata whatsoever']),
        ]
        plugin = PageContextPlugin()

        for i, (lines, context, data) in enumerate(testdata):
            self.assertEqual((context, data),
                             plugin.simple_style(lines),
                             'Test Data No. %d failed' % i)

    def test_multimarkdown_style(self):
        testdata = [
            (['Author : Me',
              'Content: Awesome',
              '',
              'Here comes the content'],
             {'author': 'Me', 'content': 'Awesome'},
             ['Here comes the content']),

            (['---',  # fenced
              'Author : Me',
              'Content: Awesome',
              '---',
              'Here comes the content'],
             {'author': 'Me', 'content': 'Awesome'},
             ['Here comes the content']),

            (['Multiline: in two',
              ' lines',
              '',
              'Here comes the content'],
             {'multiline': 'in two lines'},
             ['Here comes the content']),

            (['Multiline: in two',
              'lines',  # not indented
              '',
              'Here comes the content'],
             {'multiline': 'in two lines'},
             ['Here comes the content']),

            (['Multiline: in',
              '           three',
              '           lines',
              '',
              'Here comes the content'],
             {'multiline': 'in three lines'},
             ['Here comes the content']),

            (['Multiline: in two lines',
              '           with: colon',
              '',
              'Here comes the content'],
             {'multiline': 'in two lines with: colon'},
             ['Here comes the content']),

            (['',  # file starts with a blank line
              'Todays motto: whatever'],
             {},  # no context data
             ['', 'Todays motto: whatever']),  # blank line preserved

            (['This file has',
              'no metadata whatsoever'],
             {},
             ['This file has', 'no metadata whatsoever']),
        ]
        plugin = PageContextPlugin()

        for i, (lines, context, data) in enumerate(testdata):
            self.assertEqual((context, data),
                             plugin.multimarkdown_style(lines),
                             'Test Data No. %d failed' % i)

