#coding:utf-8
import json
import logging


logger = logging.getLogger(__name__)


class ConfigFile(object):
    """
    A single config file, as present on the filesystem.
    """
    _unsaved = None

    def __init__(self, path):
        self.path = path
        self.load()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self._unsaved = True

    def has_key(self, key):
        return key in self._data

    def load(self):
        self._data = {}
        try:
            self._data = json.load(open(self.path, 'rU'))
            self._unsaved = False
        except IOError:
            logger.warning('No configuration file found at {0}'.format(self.path))
        except ValueError, e:
            logger.error('Unable to load configuration at %s', self.path)
            logger.error('Error message: %s', e)

    def write(self):
        if self._unsaved:
            json.dump(self._data, open(self.path, 'w'), sort_keys=True, indent=4, separators=(',', ': '))
            self._unsaved = False
        logger.debug('Saved configuration at {0}'.format(self.path))
