#coding:utf-8

class CacheDurationPlugin(object):
    def preDeploy(self, site):
        """
        Load the cache duration from the config
        """
        self.cache_duration = site.config.get("cache-duration")

    def preDeployFile(self, file):
        """
        Set the cache duration expiry on the file
        """
        if self.cache_duration is not None:
            file.headers['Cache-Control'] = 'max-age={0}'.format(self.cache_duration)