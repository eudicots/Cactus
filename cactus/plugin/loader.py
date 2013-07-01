#coding:utf-8

import os
import sys
import imp
import logging

from cactus.plugin import defaults
from cactus.plugin.builtin import context
from cactus.utils.filesystem import fileList


BUILTIN_PLUGINS = [context.plugin]


class PluginLoader(object):
    def __init__(self, plugin_path):
        self.plugin_path = plugin_path

    def load(self):
        """
        Load all the plugins found
        """
        plugins = []

        # Load user plugins
        for plugin_path in fileList(self.plugin_path):
            if self._is_plugin(plugin_path):
                custom_plugin = self._load_plugin_module(plugin_path)
                custom_plugin.builtin = False
                plugins.append(custom_plugin)

        # Load cactus internal plugins
        for builtin_plugin in BUILTIN_PLUGINS:
            builtin_plugin.builtin = True
            plugins.append(builtin_plugin)

        # Load defaults
        for plugin in plugins:
            self._initialize_plugin(plugin)

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

    def _load_plugin_module(self, plugin_path):
        """
        Load plugin_path as a plugin
        """
        module_name = "plugin_{0}".format(os.path.splitext(os.path.basename(plugin_path))[0])

        try:
            plugin_module = imp.load_source(module_name, plugin_path)
        except Exception, e:
            logging.info('Error: Could not load plugin at path %s\n%s' % (plugin_path, e))
            sys.exit()

        return plugin_module

    def _initialize_plugin(self, plugin):
        """
        Load default methods and attributes on the plugin module
        """
        # Load default attributes
        for attr in defaults.DEFAULTS + ['ORDER']:
            if not hasattr(plugin, attr):
                setattr(plugin, attr, getattr(defaults, attr))

        # Name the plugin
        if not hasattr(plugin, "plugin_name"):
            if hasattr(plugin, "__name__"):
                plugin.plugin_name = plugin.__name__
            elif hasattr(plugin, "__class__"):
                plugin.plugin_name = plugin.__class__.__name__
            else:
                plugin.plugin_name = "anonymous"