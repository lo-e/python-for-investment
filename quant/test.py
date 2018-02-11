# -- coding: utf-8 --

import pandas as pd
import tushare as ts
from datetime import time, timedelta
import multiprocessing


def testMulti(args):
    print args
    return 1

if __name__ == '__main__':
    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    l = []

    settingList = {'openLen': 2}
    for setting in settingList:
        l.append(pool.apply_async(testMulti, ('a')))
    pool.close()
    pool.join()

    # 显示结果
    resultList = [res.get() for res in l]
    print resultList