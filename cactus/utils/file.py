#coding:utf-8
import os
import gzip
import io
import hashlib
import subprocess

from six import text_type, BytesIO

from cactus.utils.helpers import checksum


class FakeTime:
    """
    Monkey-patch gzip.time to avoid changing files every time we deploy them.
    """
    def time(self):
        return 1111111111.111


def compressString(s):
    """Gzip a given string."""

    gzip.time = FakeTime()

    zbuf = BytesIO()
    zfile = gzip.GzipFile(mode='wb', compresslevel=9, fileobj=zbuf)
    zfile.write(s)
    zfile.close()
    return zbuf.getvalue()


def fileSize(num):
    for x in ['b', 'kb', 'mb', 'gb', 'tb']:
        if num < 1024.0:
            return "%.0f%s" % (num, x)
        num /= 1024.0

def calculate_file_checksum(path):
    """
    Calculate the MD5 sum for a file:
    Read chunks of a file and update the hasher.
    Returns the hex digest of the md5 hash.
    """
    hasher = hashlib.md5()
    with io.FileIO(path, 'r') as fp:
        while True:
            buf = fp.read(65536)
            if not buf:
                break
            hasher.update(buf)
    return hasher.hexdigest()

def file_changed_hash(path):
    info = os.stat(path)
    hashKey = text_type(info.st_mtime) + text_type(info.st_size)
    return checksum(hashKey.encode('utf-8'))
