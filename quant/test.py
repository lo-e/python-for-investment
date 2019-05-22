# -- coding: utf-8 --

import pymongo
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
from vnpy.trader.app.ctaStrategy.ctaBase import DAILY_DB_NAME
from datetime import datetime
from vnpy.trader.app.ctaStrategy.stgEarningManager import stgEarningManager
from collections import OrderedDict
import matplotlib.pyplot as plt
import pandas as pd
import rqdatac as rq
from rqdatac import *
import re
from csv import DictReader
import pandas as pd

class SliceIdGenerator:
    """slice id生成器"""
    def __init__(self):
        self.__ch = 'aaaaaaaaa`'

    def getNextSliceId(self):
        ch = self.__ch
        j = len(ch) - 1
        while j >= 0:
            cj = ch[j]
            if cj != 'z':
                ch = ch[:j] + chr(ord(cj) + 1) + ch[j+1:]
                break
            else:
                ch = ch[:j] + 'a' + ch[j+1:]
                j = j -1
        self.__ch = ch
        return self.__ch


if __name__ == '__main__':
    generator = SliceIdGenerator();
    i = 0
    while i < 10:
        ch = generator.getNextSliceId()
        print ch
        i += 1

