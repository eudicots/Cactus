#coding:utf-8
import os
import time
import threading
import logging

import six

from cactus.utils.filesystem import fileList
from cactus.utils.network import retry

class PollingListener(object):
    def __init__(self, path, f, delay = .5, ignore = None):
        self.path = path
        self.f = f
        self.delay = delay
        self.ignore = ignore
        self._pause = False
        self._checksums = {}

    def checksums(self):
        checksumMap = {}

        for f in fileList(self.path):

            if f.startswith('.'):
                continue

            if self.ignore and self.ignore(f):
                continue

            try:
                checksumMap[f] = int(os.stat(f).st_mtime)
            except OSError:
                continue

        return checksumMap

    def run(self):
        # self._loop()
        t = threading.Thread(target=self._loop)
        t.daemon = True
        t.start()

    def pause(self):
        self._pause = True

    def resume(self):
        self._checksums = self.checksums()
        self._pause = False

    def _loop(self):
        self._checksums = self.checksums()

        while True:
            self._run()

    @retry((Exception,), tries = 5, delay = 0.5)
    def _run(self):
        if not self._pause:
            oldChecksums = self._checksums
            newChecksums = self.checksums()

            result = {
                'added': [],
                'deleted': [],
                'changed': [],
            }

            for k, v in six.iteritems(oldChecksums):
                if k not in newChecksums:
                    result['deleted'].append(k)
                elif v != newChecksums[k]:
                    result['changed'].append(k)

            for k, v in six.iteritems(newChecksums):
                if k not in oldChecksums:
                    result['added'].append(k)

            result['any'] = result['added'] + result['deleted'] + result['changed']

            if result['any']:
                self._checksums = newChecksums
                self.f(result)

        time.sleep(self.delay)
