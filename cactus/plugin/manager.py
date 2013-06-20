#coding:utf-8
import functools

from cactus.plugin.loader import PluginLoader
from cactus.plugin import defaults


ACCEPTED_PREBUILD_ERROR_MESSAGES = [
    "preBuildPage() takes exactly 3 arguments (4 given)",
    "preBuildPage() takes exactly 4 arguments (3 given)",  # In practice, this can't show up.
]


class PluginManager(object):
    def __init__(self, plugin_path):
        self.loader = PluginLoader(plugin_path)
        self.reload()

        for plugin_method in defaults.DEFAULTS:
            if not hasattr(self, plugin_method):
                setattr(self, plugin_method, functools.partial(self.call, plugin_method))

    def reload(self):
        self.plugins = self.loader.load()

    def call(self, method, *args, **kwargs):
        """
        Call each plugin
        """
        for plugin in self.plugins:
            _meth = getattr(plugin, method)
            _meth(*args, **kwargs)

    def preBuildPage(self, site, page, context, data):
        """
        Special call as we have changed the API for this.
        """
        for plugin in self.plugins:
            arg_lists = [[site, page, context, data], [page, context, data]]
            for arg_list in arg_lists:
                try:  # TODO: Use `import inspect`
                    context, data = plugin.preBuildPage(*arg_list)
                except TypeError as e:
                    if e.args[0] in ACCEPTED_PREBUILD_ERROR_MESSAGES:
                        continue  # Wrong calling convention: try again
                    raise
                else:
                    break  # Correct calling convention: do not run again.

        return context, data