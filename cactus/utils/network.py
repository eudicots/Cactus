import logging
import time
import urllib2
from cactus.utils.helpers import multiMap


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2):
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    try_one_last_time = False
                    break
                except ExceptionToCheck, e:
                    logging.warning("%s, Retrying in %.1f seconds..." % (str(e), mdelay))
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
            response = urllib2.urlopen(url, timeout = 1)
            return True
        except urllib2.URLError as err:
            pass
        return False

    return True in multiMap(check, [
        'http://www.google.com',
        'http://www.apple.com'])