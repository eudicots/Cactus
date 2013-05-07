from functools import partial
import multiprocessing.pool


def multiMap(f, items, workers = 8):
    pool = multiprocessing.pool.ThreadPool(workers)
    return pool.map(f, items)


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