#coding:utf-8
import cStringIO
import gzip

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

    zbuf = cStringIO.StringIO()
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
    Calculate the MD5 sum for a file (needs to fit in memory)
    """
    with open(path, 'rb') as f:
        return checksum(f.read())