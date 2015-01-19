#coding:utf-8
from __future__ import print_function
import sys
import logging
import multiprocessing.pool


PARALLEL_AGGRESSIVE = 2
PARALLEL_CONSERVATIVE = 1
PARALLEL_DISABLED = 0

def multiMap(f, items, workers = 8):

    # Code in GCS engine +/- depends on this being threads
    pool = multiprocessing.pool.ThreadPool(workers)

    # Simple wrapper to provide decent tracebacks
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            pool.join()
            sys.exit()

    return pool.map(wrapper, items)
