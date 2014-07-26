#coding:utf-8
from cactus.contrib.external.closure import ClosureJSOptimizer
from cactus.contrib.external.yui import YUICSSOptimizer


def preBuild(site):
    """
    Registers optimizers as requested by the configuration.
    Be sure to read the plugin to understand and use it.
    """

    # Inspect the site configuration, and retrieve an `optimize` list.
    # This lets you configure optimization selectively.
    # You may want to use one configuration for staging with no optimizations, and one
    # configuration for production, with all optimizations.
    optimize = site.config.get("optimize", [])

    if "js" in optimize:
        # If `js` was found in the `optimize` key, then register our JS optimizer.
        # This uses closure, but you could use cactus.contrib.external.yui.YUIJSOptimizer!
        site.external_manager.register_optimizer(ClosureJSOptimizer)

    if "css" in optimize:
        # Same thing for CSS.
        site.external_manager.register_optimizer(YUICSSOptimizer)

    # Add your own types here!
