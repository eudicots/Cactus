#coding:utf-8
import json
import logging


class ConfigFile(object):
    """
    A single config file, as present on the filesystem.
    """

    def __init__(self, path):
        self.path = path
        self.load()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def has_key(self, key):
        return key in self._data

    def load(self):
        try:
            self._data = json.load(open(self.path, 'rU'))
        except IOError:
            logging.info('No configuration file found at {0}'.format(self.path))
            self._data = {}
        except Exception:
            logging.warning('Unable to load configuration at {0}'.format(self.path))
            self._data = {}

    def write(self):
        json.dump(self._data, open(self.path, 'w'), sort_keys=True, indent=4, separators=(',', ': '))
        logging.debug('Saved configuration at {0}'.format(self.path))