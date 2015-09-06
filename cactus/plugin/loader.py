#coding:utf-8
import os
import sys
import imp
import logging

from cactus.plugin import defaults
from cactus.utils.filesystem import fileList


logger = logging.getLogger(__name__)


class BasePluginsLoader(object):
    def load(self):
        raise NotImplementedError("Subclasses must implement load")

    def _initialize_plugin(self, plugin):
        """
        :param plugin: A plugin to initialize.
        :returns: An initialized plugin with all default methods set.
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


class ObjectsPluginLoader(BasePluginsLoader):
    """
    Loads the plugins objects passed to this loader.
    """
    def __init__(self, plugins):
        """
        :param plugins: The list of plugins this loader should load.
        """
        self.plugins = plugins

    def load(self):
        """
        :returns: The list of plugins loaded by this loader.
        """
        plugins = []

        # Load cactus internal plugins
        for builtin_plugin in self.plugins:
            self._initialize_plugin(builtin_plugin)
            plugins.append(builtin_plugin)

        return plugins


class CustomPluginsLoader(BasePluginsLoader):
    """
    Loads all the plugins found at the path passed.
    """

    def __init__(self, plugin_path):
        """
        :param plugin_path: The path where the plugins should be loaded from.
        """
        self.plugin_path = plugin_path

    def load(self):
        """
        :returns: The list of plugins loaded by this loader.
        """
        plugins = []

        # Load user plugins
        for plugin_path in fileList(self.plugin_path):
            if self._is_plugin_path(plugin_path):
                custom_plugin = self._load_plugin_path(plugin_path)
                if custom_plugin:
                    self._initialize_plugin(custom_plugin)
                    plugins.append(custom_plugin)


        return plugins

    def _is_plugin_path(self, plugin_path):
        """
        :param plugin_path: A path where to look for a plugin.
        :returns: Whether this path looks like an enabled plugin.
        """
        if not plugin_path.endswith('.py'):
            return False

        if 'disabled' in plugin_path:
            return False

        return True

    def _load_plugin_path(self, plugin_path):
        """
        :param plugin_path: A path to load as a plugin.
        :returns: A plugin module.
        """
        module_name = "plugin_{0}".format(os.path.splitext(os.path.basename(plugin_path))[0])

        try:
            return imp.load_source(module_name, plugin_path)
        except Exception as e:
            logger.warning('Could not load plugin at path %s: %s' % (plugin_path, e))
            return None

            # sys.exit()
