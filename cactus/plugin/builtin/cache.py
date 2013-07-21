#coding:utf-8

class CacheDurationPlugin(object):
    """
    A plugin to make the default cache expiry configurable via a "cache-duration" configuration setting
    """

    def preDeploy(self, site):
        """
        Load the cache duration from the config
        """
        self.cache_duration = site.config.get("cache-duration")

    def preDeployFile(self, file):
        """
        Set the cache duration expiry on the file
        """
        if self.cache_duration is not None and not file.is_fingerprinted:
            file.cache_control = self.cache_duration
