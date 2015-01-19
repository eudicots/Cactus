#coding:utf-8

class ContextPlugin(object):
    """
    A plugin to manage custom context via config files.

    The context can be made available via a "context" key in config files.
    """

    def preBuild(self, site):
        """
        Load the context from the config
        """
        self.context = site.config.get("context", {}, nested=True)

    def preBuildPage(self, page, context, data):
        """
        Update the page context with the config context
        """
        context.update(self.context)

        return context, data


plugin = ContextPlugin()
