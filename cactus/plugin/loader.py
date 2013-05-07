#coding:utf-8

import os
import sys
import imp
import logging

from cactus.plugin import defaults
from cactus.utils.filesystem import fileList


class PluginLoader(object):
    def __init__(self, plugin_path):
        self.plugin_path = plugin_path

    def load(self):
        """
        Load all the plugins found
        """
        plugins = []

        for plugin_path in fileList(self.plugin_path):
            if self._is_plugin(plugin_path):
                plugins.append(self._load_plugin(plugin_path))

        return sorted(plugins, key=lambda plugin: plugin.ORDER)

    def _is_plugin(self, plugin_path):
        """
        Whether this path looks like a plugin.
        """
        if not plugin_path.endswith('.py'):
            return False

        if 'disabled' in plugin_path:
            return False

        return True

    def _load_plugin(self, plugin_path):
        """
        Load plugin_path as a plugin
        """
        module_name = "plugin_{0}".format(os.path.splitext(os.path.basename(plugin_path))[0])

        try:
            plugin_module = imp.load_source(module_name, plugin_path)
        except Exception, e:
            logging.info('Error: Could not load plugin at path %s\n%s' % (plugin_path, e))
            sys.exit()

        self._load_defaults(plugin_module)

        return plugin_module

    def _load_defaults(self, plugin_module):
        """
        Load default methods and attributes on the plugin module
        """
        for attr in defaults.DEFAULTS + ['ORDER']:
            if not hasattr(plugin_module, attr):
                setattr(plugin_module, attr, getattr(defaults, attr))