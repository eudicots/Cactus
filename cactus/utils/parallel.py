#coding:utf-8
import multiprocessing.pool

PARALLEL_AGGRESSIVE = 2
PARALLEL_CONSERVATIVE = 1
PARALLEL_DISABLED = 0


def multiMap(f, items, workers = 8):
    pool = multiprocessing.pool.ThreadPool(workers)  # Code in GCS engine +/- depends on this being threads
    return pool.map(f, items)