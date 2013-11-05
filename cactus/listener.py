#coding:utf-8
import os
import time
import threading
import logging

from cactus.utils.filesystem import fileList
from cactus.utils.network import retry

try:
    from fsevents import Observer, Stream
    USE_FSEVENTS = True
except ImportError, e:
    USE_FSEVENTS = False
    logging.debug("Not using fsevents: %s", e)

# Wrapper that supports streams around single files
def createStream(path, callback):

    if not os.path.isdir(path):
        
        def cb(event):
            if event.name == path: 
                callback(event)
        
        return Stream(cb, os.path.dirname(path), file_events=True)
    else:
        return Stream(callback, path, file_events=True)


class MacListener(object):
    def __init__(self, path, f, ignore = None):
        
        logging.info("Using FSEvents")
        
        self.path = path
        self.f = f
        self.ignore = ignore
        
        self._paused = False
        
        self.observer = Observer()
        self.observer.daemon = True

        self.observer.schedule(createStream(self.path, self._update))
        
        # Start an extra listener for all symlinks
        for path in fileList(self.path):
            if os.path.islink(path):
                self.observer.schedule(createStream(
                    os.path.realpath(path), self._update))
        
    def run(self):
        self.observer.start()

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
    
    def stop():
        self.observer.stop()
    
    def _update(self, event):
        
        if self._paused is True:
            return
        
        path = event.name
        
        if self.ignore and self.ignore(path):
            return
        
        logging.info("Changed: %s", path)

        result = {
            'added': [],
            'deleted': [],
            'changed': [],
        }
        
        # TODO We cannot detect added yet
        if os.path.exists(path):
            result["changed"].append(path)
        else:
            result["deleted"].append(path)
        
        self.f(result)

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

            for k, v in oldChecksums.iteritems():
                if k not in newChecksums:
                    result['deleted'].append(k)
                elif v != newChecksums[k]:
                    result['changed'].append(k)

            for k, v in newChecksums.iteritems():
                if k not in oldChecksums:
                    result['added'].append(k)

            result['any'] = result['added'] + result['deleted'] + result['changed']

            if result['any']:
                self._checksums = newChecksums
                self.f(result)

        time.sleep(self.delay)
        
if USE_FSEVENTS:
    Listener = MacListener
else:
    Listener = PollingListener
