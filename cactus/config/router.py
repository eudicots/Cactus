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

    def get(self, key, default=None):
        """
        Retrieve a config key from the first config that has it.
        Return default if no config has it.
        """
        for config in self.configs:
            if config.has_key(key):
                logging.debug("Retrieved %s from %s", key, config.path)
                return config.get(key)
        return default

    def set(self, key, value):
        """
        Write a config key from the first config that has it.

        If none do, write it to the first one.
        """
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