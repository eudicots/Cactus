#coding:utf-8
import json
import logging


class ConfigFile(object):
    """
    A single config file, as present on the filesystem.
    """
    _dirty = None

    def __init__(self, path):
        self.path = path
        self.load()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self._dirty = True

    def has_key(self, key):
        return key in self._data

    def load(self):
        try:
            self._data = json.load(open(self.path, 'rU'))
            self._dirty = False
        except IOError:
            logging.info('No configuration file found at {0}'.format(self.path))
            self._data = {}
        except Exception:
            logging.warning('Unable to load configuration at {0}'.format(self.path))
            self._data = {}

    def write(self):
        if self._dirty:
            json.dump(self._data, open(self.path, 'w'), sort_keys=True, indent=4, separators=(',', ': '))
            self._dirty = False
        logging.debug('Saved configuration at {0}'.format(self.path))