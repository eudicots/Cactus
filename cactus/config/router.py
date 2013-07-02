#coding:utf-8
import logging
from cactus.config.file import ConfigFile


class ConfigRouter(object):
    """
    A router to manage a series of config files.
    """

    def __init__(self, paths):
        """
        Load all the config files passed.
        Make sure not to load the same one twice
        """
        self.configs = []

        loaded_paths = set()
        for path in paths:
            if path not in loaded_paths:
                self.configs.append(ConfigFile(path))
                loaded_paths.add(path)

        logging.debug("Loaded configs: %s", ', '.join([config.path for config in self.configs]))


    def _get_nested(self, key, default=None):
        assert isinstance(default, dict)  # Don't shoot yourself in the foot.

        output = {}
        for config in reversed(self.configs):
            output.update(config.get(key, default))
            logging.debug("Retrieving %s from %s", key, config.path)

        return output

    def _get_first(self, key, default=None):
        for config in self.configs:
            if config.has_key(key):
                logging.debug("Retrieved %s from %s", key, config.path)
                return config.get(key)

        return default

    def get(self, key, default=None, nested=False):
        """
        Retrieve a config key from the first config that has it.
        Return default if no config has it.
        """
        logging.debug("Searching for %s (nested:%s)", key, nested)
        if nested:
            return self._get_nested(key, default)
        else:
            return self._get_first(key, default)


    def set(self, key, value):
        """
        Write a config key from the first config that has it.

        If none do, write it to the first one.
        """
        if not self.configs:
            logging.warn("Discarding set %s=%s: no config files available", key, value)
            return

        write_to = None

        for config in self.configs:
            if config.has_key(key):
               write_to = config
        if write_to is None:
            write_to = self.configs[0]

        write_to.set(key, value)
        logging.debug("Set %s in %s", key, write_to.path)

    def write(self):
        """
        Write the config files to the filesystem.
        """
        for config in self.configs:
            config.write()