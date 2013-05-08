import json
import logging


class Config(object):
    def __init__(self, path):
        self.path = path
        self.load()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def load(self):
        try:
            self._data = json.load(open(self.path, 'r'))
        except Exception:
            logging.warning('Unable to load configuration at {0}'.format(self.path))
            self._data = {}

    def write(self):
        json.dump(self._data, open(self.path, 'w'), sort_keys = True, indent = 4)