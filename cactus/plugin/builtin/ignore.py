#coding:utf-8
import fnmatch

class IgnorePatternsPlugin(object):
    """
    Define configurable ignore patterns for static files and pages
    """
    def preBuild(self, site):
        """
        Load the ignore patterns from the site config
        """
        self.ignore_patterns = site.config.get('ignore', [])

    def preBuildPage(self, page, context, data):
        if not self.accept_path(page.source_path):
            page.discarded = True
        return context, data


    def preBuildStatic(self, static):
        if not self.accept_path(static.path):
            static.discard()

    def accept_path(self, path):
        """
        :param path: A path to be tested
        :returns: Whether this path can be includes in the build
        """
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path, pattern):
                return False
        return True
