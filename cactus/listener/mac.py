#coding:utf-8
import os
import time
import threading
import logging

from ctypes import *

from cactus.utils.filesystem import fileList
from cactus.utils.network import retry

from fsevents import Observer, Stream

class struct_timespec(Structure):
    _fields_ = [('tv_sec', c_long), ('tv_nsec', c_long)]

class struct_stat64(Structure):
    _fields_ = [
        ('st_dev', c_int32),
        ('st_mode', c_uint16),
        ('st_nlink', c_uint16),
        ('st_ino', c_uint64),
        ('st_uid', c_uint32),
        ('st_gid', c_uint32),
        ('st_rdev', c_int32),
        ('st_atimespec', struct_timespec),
        ('st_mtimespec', struct_timespec),
        ('st_ctimespec', struct_timespec),
        ('st_birthtimespec', struct_timespec),
        ('dont_care', c_uint64 * 8)
    ]

libc = CDLL('/usr/lib/libc.dylib')
stat64 = libc.stat64
stat64.argtypes = [c_char_p, POINTER(struct_stat64)]

# OS-X only function to get actual creation date
def get_creation_time(path):
    buf = struct_stat64()
    rv = stat64(path, pointer(buf))
    if rv != 0:
        raise OSError("Couldn't stat file %r" % path)
    return buf.st_birthtimespec.tv_sec


def createStream(real_path, link_path, callback):

    def cb(event):

        if not os.path.isdir(link_path):
            event.name = link_path
        else:
            translated_path = os.path.join(link_path, os.path.relpath(event.name, real_path))
            event.name = translated_path

        callback(event)

    return Stream(cb, real_path, file_events=True)


class FSEventsListener(object):
    def __init__(self, path, f, ignore = None):

        logging.info("Using FSEvents")

        self.path = path
        self.f = f
        self.ignore = ignore

        self.observer = Observer()
        self.observer.daemon = True

        self._streams = []
        self._streams.append(createStream(self.path, path, self._update))

        self._streamed_folders = [self.path]

        def add_stream(p):
            if p in self._streamed_folders:
                return
            self._streams.append(
                createStream(p, file_path, self._update))
            self._streamed_folders.append(p)

        # Start an extra listener for all symlinks
        for file_path in fileList(self.path, folders=True):
            if os.path.islink(file_path):
                if os.path.isdir(file_path):
                    add_stream(os.path.realpath(file_path))
                else:
                    add_stream(os.path.dirname(os.path.realpath(file_path)))

    def run(self):
        self.resume()
        self.observer.start()

    def pause(self):
        logging.debug("MacListener.PAUSE")

        for stream in self._streams:
            self.observer.unschedule(stream)

    def resume(self):
        logging.debug("MacListener.RESUME")

        for stream in self._streams:
            self.observer.schedule(stream)

    def stop():
        self.observer.stop()

    def _update(self, event):

        path = event.name

        if self.ignore and self.ignore(path):
            return

        logging.debug("MacListener.update %s", event)

        result = {
            'added': [],
            'deleted': [],
            'changed': [],
        }

        if os.path.exists(path):

            seconds_since_created = int(time.time()) - get_creation_time(os.path.realpath(path))

            if seconds_since_created < 1.0:
                result["added"].append(path)
            else:
                result["changed"].append(path)
        else:
            result["deleted"].append(path)

        self.f(result)
