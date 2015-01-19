#coding:utf-8

class VirtualPaths(object):
    def __init__(self, obj, mapping):
        self.obj = obj
        self.mapping = mapping

    def __getitem__(self, item):

        return getattr(self.obj, self.mapping[item])


class CompatibilityLayer(object):
    """
    Ensure backwards compatibility with older versions of Cactus.
    """
    mapping = {}

    @property
    def paths(self):
        return VirtualPaths(self, self.mapping)


class SiteCompatibilityLayer(CompatibilityLayer):
    mapping = {
        'build': 'build_path',
        'pages': 'page_path',
        'plugins': 'plugin_path',
        'templates': 'template_path',
        'static': 'static_path',
        'script': 'script_path',
    }


class PageCompatibilityLayer(CompatibilityLayer):
    mapping = {
        'full': 'full_source_path',
        'full-build': 'full_build_path',
    }

    @property
    def path(self):
        return self.source_path


class StaticCompatibilityLayer(CompatibilityLayer):
    mapping = {
        'full': 'full_source_path',
        'full-build': 'full_build_path',
    }
