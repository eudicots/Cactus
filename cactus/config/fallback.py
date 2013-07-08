#coding:utf-8
import logging


class ConfigFallback(object):
    """
    A transient fallback config.
    This config does not store anything to the filesystem.
    """
    def __init__(self):
        self.cnf = {}

    @property
    def path(self):
        return "@fallback"

    def get(self, key, default=None):
        return self.cnf.get(key, default)

    def set(self, key, value):
        self.cnf[key] = value

    def has_key(self, key):
        return key in self.cnf

    def write(self):
        logging.warn("Using config fallback, discarding config values: [%s]", ', '.join(self.cnf.keys()))
