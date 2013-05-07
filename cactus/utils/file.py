#coding:utf-8
import cStringIO
import gzip


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