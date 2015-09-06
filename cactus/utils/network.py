#coding:utf-8
import logging
import time
from six.moves import urllib

from cactus.utils.parallel import multiMap


logger = logging.getLogger(__name__)


def retry(exceptions, tries=4, delay=3, backoff=2):
    """
    Retry execution in case we fail on one of the exceptions
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    logger.warning("%s, Retrying in %.1f seconds..." % (str(e), mdelay))
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return

        return f_retry  # true decorator

    return deco_retry


def internetWorking():
    def check(url):
        try:
            response = urllib.request.urlopen(url, timeout = 1)
            return True
        except urllib.error.URLError as err:
            pass
        return False

    return True in multiMap(check, [
        'http://www.google.com',
        'http://www.apple.com'])
