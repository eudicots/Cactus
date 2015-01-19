import hashlib
from functools import partial

import six


class CaseInsensitiveDict(dict):
    def __init__(self, obj = None, **kwargs):
        if obj is not None:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    self[k] = v
            else:
                for k, v in obj:
                    self[k] = v

        for k, v in kwargs.items():
            self[k] = v

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())

    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(key.lower())

    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(key.lower())

    def pop(self, key):
        return super(CaseInsensitiveDict, self).pop(key.lower())


class memoize(object):
    """
    Memoize the return parameters of a function.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)

    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            cache = obj.__cache
        except AttributeError:
            cache = obj.__cache = {}
        key = (self.func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res


if six.PY3:
    def map_apply(fn, iterable):
        return list(map(fn, iterable))
else:
    map_apply = map


def checksum(s):
    """
    Calculate the checksum of a string.
    Should eventually support files too.

    We use MD5 because S3 does.
    """
    return hashlib.md5(s).hexdigest()


def get_or_prompt(config, key, prompt_fn, *args, **kwargs):
    """
    :param config: The configuration object to get the value from
    :param key: The configuration key to retrieve
    :type key: str
    :param prompt_fn: The prompt function to use to prompt the value
    :param args: Extra arguments for the prompt function
    :param kwargs: Extra keyword arguments for hte prompt function
    """
    value = config.get(key)
    if value is None:
        value = prompt_fn(*args, **kwargs)
        config.set(key, value)
    return value
