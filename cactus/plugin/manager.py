#coding:utf-8
import functools

from cactus.utils.internal import getargspec
from cactus.plugin import defaults


class PluginManager(object):
    def __init__(self, site, loaders):
        self.site = site
        self.loaders = loaders
        self.reload()

        for plugin_method in defaults.DEFAULTS:
            if not hasattr(self, plugin_method):
                setattr(self, plugin_method, functools.partial(self.call, plugin_method))

    def reload(self):
        plugins = []
        for loader in self.loaders:
            plugins.extend(loader.load())

        self.plugins = sorted(plugins, key=lambda plugin: plugin.ORDER)

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

        We have two calling conventions:
        - The new one, which passes page, context, data
        - The deprecated one, which also passes the site (Now accessible via the page)
        """
        for plugin in self.plugins:
            # Find the correct calling convention
            new = [page, context, data]
            deprecated = [site, page, context, data]
            arg_lists = dict((len(l), l) for l in [deprecated, new])

            try:
                # Try to find the best calling convention
                n_args = len(getargspec(plugin.preBuildPage).args)
                # Just use the new calling convention if there's fancy usage of
                # *args, **kwargs that we can't control.
                arg_list = arg_lists.get(n_args, new)
            except NotImplementedError:
                # If we can't get the number of args, use the new one.
                arg_list = new

            # Call with the best calling convention we have.
            # If that doesn't work, then we'll let the error escalate.
            context, data = plugin.preBuildPage(*arg_list)

        return context, data
